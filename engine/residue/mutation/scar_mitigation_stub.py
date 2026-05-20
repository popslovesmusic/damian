import uuid

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-154"
SYSTEM_NAME = "scar_mitigation_stub"


def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass


def estimate_mitigation_cost(mitigation_effort=1):
    """
    Cost model (MVP): bounded, non-free mitigation.

    Effort is an integer step that converts into a small mitigation credit.
    """
    effort = max(1, int(mitigation_effort))
    # 2 shards per effort step, increasing slightly to preserve Tower hostility.
    return int(round(2 * effort + max(0, effort - 1)))


def apply_scar_mitigation(node_id, floor_id, scarring_record, mitigation_credit=0.0, debug=False):
    """
    Applies bounded mitigation to an existing scarring record.

    Guarantees:
    - mitigation reduces pressure but cannot erase history
    - scar intensity has a minimum floor (no total erasure)
    """
    base_intensity = float((scarring_record or {}).get("scar_intensity", 0.0) or 0.0)
    base_intensity = max(0.0, min(1.0, base_intensity))
    base_hazard = float((scarring_record or {}).get("hazard_bias", 0.0) or 0.0)
    base_hazard = max(0.0, min(1.0, base_hazard))

    credit = float(mitigation_credit or 0.0)
    credit = max(0.0, min(0.5, credit))

    # Minimum scar floor prevents erasure. If a node is scarred, it stays scarred.
    min_intensity = 0.10
    mitigated_intensity = max(min_intensity, base_intensity - credit)
    mitigated_intensity = float(round(max(0.0, min(1.0, mitigated_intensity)), 4))

    # Hazard bias is derived from intensity in scarring stub; keep consistent shape.
    mitigated_hazard = float(round(mitigated_intensity * 0.6, 4))

    record = {
        "mitigation_id": f"mit_{uuid.uuid4()}",
        "node_id": node_id,
        "floor_id": int(floor_id),
        "base_scar_intensity": float(round(base_intensity, 4)),
        "mitigated_scar_intensity": mitigated_intensity,
        "base_hazard_bias": float(round(base_hazard, 4)),
        "mitigated_hazard_bias": mitigated_hazard,
        "mitigation_credit_used": float(round(min(credit, max(0.0, base_intensity - min_intensity)), 4)),
        "minimum_floor_enforced": True,
        "bounded_flags_clean": True
    }

    _log_debug_event(
        "INFO",
        "ScarMitigated",
        f"Node {node_id} scar: {base_intensity} -> {mitigated_intensity}",
        record,
        debug_enabled=debug,
    )

    return record


def summarize_mitigation(record):
    if not record:
        return "No scar mitigation record."
    return (
        f"Scar Mitigation (Floor {record.get('floor_id')}, Node {record.get('node_id')}): "
        f"{record.get('base_scar_intensity', 0.0):.2f}->{record.get('mitigated_scar_intensity', 0.0):.2f} "
        f"(-{record.get('mitigation_credit_used', 0.0):.2f})."
    )

