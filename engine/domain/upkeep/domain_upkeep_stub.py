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

# Territorial instability (Stage-018)
try:
    from engine.domain.instability import territorial_instability_stub
    _instability_available = True
except ImportError:
    _instability_available = False

# Import json_save_manager for validation
try:
    from engine.save.runtime import json_save_manager
    _save_manager_available = True
except ImportError:
    _save_manager_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_UPKEEP_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/domain/upkeep/contracts/domain_upkeep_event.schema.json")

PATCH_ID = "TOWER-ENGINE-128"
SYSTEM_NAME = "domain_upkeep_stub"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass
    elif not _debug_logger_available and debug_enabled:
        print(f"DEBUG [{SYSTEM_NAME}]: {message}")

def calculate_upkeep_cost(claim, maintenance_penalty=0, debug=False):
    """
    Calculates the material upkeep cost (Stability Shards) for a claim.
    Base cost scales with floor depth.
    """
    floor_id = claim.get("floor_id", 1)
    claim_type = claim.get("claim_type", "recovery_anchor")
    
    # Base cost starts at 1 and increases every 3 floors
    base_cost = 1 + (floor_id // 3)
    
    # Type multipliers
    type_bias = {
        "recovery_anchor": 1.0,
        "supply_cache": 1.2,
        "repair_station": 1.5,
        "survivor_outpost": 2.0,
        "observation_post": 0.8
    }
    
    multiplier = type_bias.get(claim_type, 1.0)
    final_cost = int(base_cost * multiplier) + int(maintenance_penalty)
    
    # Minimum cost is 1
    return max(1, final_cost)

def process_claim_upkeep(claim, available_shards, maintenance_penalty=0, targeting_record=None, debug=False):
    """
    Processes upkeep for a single claim.
    Returns a result dict with success status and updated claim state.
    """
    previous_state = claim.get("status", "ACTIVE")
    floor_id = claim.get("floor_id", 1)
    claim_id = claim.get("claim_id", "unknown")
    
    # Merge any targeting-based penalty (if present) with caller-provided penalty.
    targeting_penalty = 0
    if isinstance(targeting_record, dict):
        targeting_penalty = int(targeting_record.get("maintenance_penalty", 0) or 0)

    total_penalty = int(maintenance_penalty) + targeting_penalty
    cost = calculate_upkeep_cost(claim, maintenance_penalty=total_penalty, debug=debug)
    
    upkeep_successful = False
    shards_deducted = 0
    current_state = previous_state
    
    if available_shards >= cost:
        upkeep_successful = True
        shards_deducted = cost
        # If was decaying or overrun, paying upkeep can restore state
        # (Though some systems might require extra for restoration, 
        # for MVP we'll just restore to ACTIVE if paid)
        current_state = "ACTIVE"
    else:
        # Failed payment triggers decay
        if previous_state == "ACTIVE":
            current_state = "DECAYING"
        elif previous_state == "DECAYING":
            current_state = "OVERRUN"
        # If already OVERRUN, stays OVERRUN
    
    event = {
        "event_id": f"upk_{uuid.uuid4()}",
        "claim_id": claim_id,
        "floor_id": floor_id,
        "shards_requested": cost,
        "shards_deducted": shards_deducted,
        "previous_state": previous_state,
        "current_state": current_state,
        "upkeep_successful": upkeep_successful,
        "bounded_flags_clean": True
    }

    instability_record = None
    if _instability_available:
        try:
            instability_record = territorial_instability_stub.calculate_territorial_instability(
                claim, targeting_record=targeting_record, upkeep_successful=upkeep_successful, debug=debug
            )
            # Persist minimal evidence on the claim for downstream reporting.
            claim["territorial_instability"] = instability_record.get("instability", 0.0)
            claim["instability_band"] = instability_record.get("instability_band", "STABLE")
        except Exception:
            instability_record = None
    
    _log_debug_event("INFO", "UpkeepProcessed", f"Upkeep for {claim_id}: {previous_state} -> {current_state}", event, debug)
    
    return {
        "ok": True,
        "upkeep_event": event,
        "updated_status": current_state,
        "shards_consumed": shards_deducted,
        "territorial_instability": instability_record,
        "summary": summarize_upkeep_event(event)
    }

def validate_upkeep_event(event, schema_path=None, debug=False):
    """Validates an upkeep event record against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _UPKEEP_SCHEMA_PATH
    return json_save_manager.validate_json(event, schema_path, debug=debug)

def summarize_upkeep_event(event):
    """Returns a human-readable summary of the upkeep event."""
    if not event:
        return "No upkeep event."
    
    success_str = "Paid" if event.get("upkeep_successful") else "NEGLECTED"
    summary = f"Upkeep [{event.get('claim_id')[:8]}]: {success_str}. "
    summary += f"Cost: {event.get('shards_deducted')}/{event.get('shards_requested')} shards. "
    summary += f"State: {event.get('previous_state')} -> {event.get('current_state')}."
    return summary
