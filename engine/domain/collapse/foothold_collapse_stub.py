import uuid

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-145"
SYSTEM_NAME = "foothold_collapse_stub"


def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass


def _band_for_collapse(level):
    if level >= 0.75:
        return "SEVERE"
    if level >= 0.35:
        return "PARTIAL"
    if level > 0.0:
        return "MINOR"
    return "NONE"


def evaluate_foothold_collapse(claim, instability_record=None, debug=False):
    """
    Derives bounded, partial collapse evidence from instability.

    Collapse is:
    - a degradable benefit reduction signal (not deletion)
    - recoverable if instability is reduced
    - identity-preserving (claim_id remains intact)
    """
    instability = float(claim.get("territorial_instability", 0.0) or 0.0)
    if isinstance(instability_record, dict):
        instability = float(instability_record.get("instability", instability) or instability)
    instability = max(0.0, min(1.0, instability))

    status = (claim.get("status", "ACTIVE") or "ACTIVE").upper()
    targeting_pressure = None
    if isinstance(instability_record, dict):
        targeting_pressure = instability_record.get("drivers", {}).get("targeting_pressure")

    # Collapse only begins past an instability threshold.
    # Level is normalized and bounded to [0, 1].
    threshold = 0.75
    if instability <= threshold:
        collapse_level = 0.0
    else:
        collapse_level = (instability - threshold) / max(1e-9, (1.0 - threshold))
        collapse_level = max(0.0, min(1.0, collapse_level))

    # If the foothold is already OVERRUN, we treat collapse evidence as present,
    # but still bounded and identity-preserving.
    if status == "OVERRUN":
        collapse_level = max(collapse_level, 0.35)

    collapse_level = float(round(collapse_level, 4))
    collapse_band = _band_for_collapse(collapse_level)

    base_recovery = float(claim.get("recovery_value", 0.0) or 0.0)
    # Partial collapse degrades effective recovery value, but never to 0 unless
    # the claim is OVERRUN (benefits lost by existing upkeep boundary).
    if status == "OVERRUN":
        effective_recovery = 0.0
    else:
        effective_recovery = base_recovery * (1.0 - (collapse_level * 0.5))
        effective_recovery = max(0.0, min(1.0, effective_recovery))
    effective_recovery = float(round(effective_recovery, 4))

    record = {
        "collapse_id": f"col_{uuid.uuid4()}",
        "claim_id": claim.get("claim_id"),
        "collapse_level": collapse_level,
        "collapse_band": collapse_band,
        "instability": float(round(instability, 4)),
        "claim_status": status,
        "effective_recovery_value": effective_recovery,
        "evidence": {
            "partial_collapse": collapse_level > 0.0,
            "benefit_degraded": (status != "OVERRUN" and effective_recovery < base_recovery),
            "targeting_pressure": targeting_pressure
        },
        "bounded_flags_clean": True
    }

    _log_debug_event(
        "INFO",
        "CollapseEvaluated",
        f"Claim {claim.get('claim_id')} collapse: {collapse_level} ({collapse_band})",
        record,
        debug_enabled=debug,
    )

    return record


def summarize_foothold_collapse(record):
    if not record:
        return "No collapse data."
    band = record.get("collapse_band", "UNKNOWN")
    return f"Foothold Collapse: {record.get('collapse_level', 0.0):.2f} ({band})."

