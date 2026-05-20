import uuid

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-143"
SYSTEM_NAME = "territorial_instability_stub"


def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass


def _band_for_instability(value):
    if value >= 0.85:
        return "CRITICAL"
    if value >= 0.65:
        return "HIGH"
    if value >= 0.35:
        return "ELEVATED"
    if value > 0.0:
        return "LOW"
    return "STABLE"


def calculate_territorial_instability(claim, targeting_record=None, upkeep_successful=None, debug=False):
    """
    Calculates bounded, recoverable territorial instability for a single foothold.

    Instability is a *scar pressure* on the claim, not deletion:
    - It rises under focused targeting and upkeep neglect.
    - It falls under successful maintenance.
    - It preserves claim identity and keeps the system recoverable.
    """
    prev = float(claim.get("territorial_instability", 0.0) or 0.0)
    prev = max(0.0, min(1.0, prev))

    targeting_pressure = 0.0
    is_destabilized = False
    maintenance_penalty = 0
    if isinstance(targeting_record, dict):
        targeting_pressure = float(targeting_record.get("targeting_pressure", 0.0) or 0.0)
        is_destabilized = bool(targeting_record.get("is_destabilized", False))
        maintenance_penalty = int(targeting_record.get("maintenance_penalty", 0) or 0)

    status = (claim.get("status", "ACTIVE") or "ACTIVE").upper()

    increase = 0.0
    decrease = 0.0

    # Sustained targeting drives instability.
    # Only meaningfully increases once the Tower is focusing the claim.
    if targeting_pressure > 0.55:
        increase += (targeting_pressure - 0.55) * 0.35

    # Neglect (failed upkeep) spikes instability.
    if upkeep_successful is False:
        increase += 0.15

    # Existing decay state is itself a destabilizer.
    if status == "DECAYING":
        increase += 0.05
    elif status == "OVERRUN":
        increase += 0.08

    # Successful maintenance reduces instability (recoverability preservation).
    if upkeep_successful is True:
        # High targeting makes recovery harder but still possible.
        recovery_factor = 0.10 + (max(0.0, 1.0 - targeting_pressure) * 0.05)
        decrease += recovery_factor

    new_value = prev + increase - decrease
    new_value = float(round(max(0.0, min(1.0, new_value)), 4))

    record = {
        "instability_id": f"inst_{uuid.uuid4()}",
        "claim_id": claim.get("claim_id"),
        "previous_instability": float(round(prev, 4)),
        "instability": new_value,
        "instability_band": _band_for_instability(new_value),
        "drivers": {
            "targeting_pressure": float(round(max(0.0, min(1.0, targeting_pressure)), 4)),
            "upkeep_successful": upkeep_successful,
            "is_destabilized": is_destabilized,
            "maintenance_penalty": maintenance_penalty,
            "claim_status": status
        },
        "bounded_flags_clean": True
    }

    _log_debug_event(
        "INFO",
        "InstabilityCalculated",
        f"Claim {claim.get('claim_id')} instability: {record['previous_instability']} -> {record['instability']}",
        record,
        debug_enabled=debug,
    )

    return record


def summarize_territorial_instability(record):
    if not record:
        return "No instability data."
    band = record.get("instability_band", "UNKNOWN")
    return f"Territorial Instability: {record.get('instability', 0.0):.2f} ({band})."

