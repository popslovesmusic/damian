import os
import json
import uuid
import datetime

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-127"
SYSTEM_NAME = "claim_targeting_stub"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass

def calculate_claim_targeting(claim, floor_reclamation_pressure, local_scarring=0.0, debug=False):
    """
    Calculates deterministic targeting pressure for a specific claim.
    """
    visibility = claim.get("visibility_pressure", 0.0)
    
    # 1. Visibility Contribution
    vis_cont = visibility * 0.7
    
    # 2. Scarring Contribution
    # Local instability makes the claim easier to target
    scar_cont = local_scarring * 0.3
    
    # 3. Reclamation Multiplier
    # Floor-wide reclamation drive escalates individual targeting
    reclamation_factor = 1.0 + (floor_reclamation_pressure * 0.5)
    
    # Aggregate
    targeting = (vis_cont + scar_cont) * reclamation_factor
    targeting = round(max(0.0, min(1.0, float(targeting))), 4)
    
    # 4. Maintenance Penalty
    # Targeted claims increase their upkeep cost
    maintenance_penalty = 0
    if targeting > 0.5:
        maintenance_penalty = 1
    if targeting > 0.8:
        maintenance_penalty = 2
        
    record = {
        "claim_id": claim.get("claim_id"),
        "targeting_pressure": targeting,
        "maintenance_penalty": maintenance_penalty,
        "contributions": {
            "visibility": round(vis_cont, 4),
            "scarring": round(scar_cont, 4),
            "reclamation_multiplier": round(reclamation_factor, 4)
        },
        "is_destabilized": targeting > 0.7,
        "bounded_flags_clean": True
    }
    
    _log_debug_event("INFO", "TargetingCalculated", f"Claim {claim.get('claim_id')} Targeting: {targeting}", record, debug)
    
    return record

def summarize_targeting(record):
    """Returns a human-readable summary of the targeting status."""
    if not record:
        return "No targeting data."
    
    status = "DESTABILIZED" if record.get("is_destabilized") else "STABLE"
    summary = f"Claim Targeting: {record.get('targeting_pressure'):.2f} ({status}). "
    summary += f"Upkeep Penalty: +{record.get('maintenance_penalty')} shards."
    return summary
