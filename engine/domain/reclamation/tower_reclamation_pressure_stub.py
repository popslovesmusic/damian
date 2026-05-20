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

# Import json_save_manager for validation
try:
    from engine.save.runtime import json_save_manager
    _save_manager_available = True
except ImportError:
    _save_manager_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_RECLAMATION_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/domain/reclamation/contracts/reclamation_pressure.schema.json")

PATCH_ID = "TOWER-ENGINE-120"
SYSTEM_NAME = "tower_reclamation_pressure_stub"

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

def get_reclamation_band(pressure):
    """Maps a pressure value to a Reclamation Band."""
    if pressure <= 0.2:
        return "STABLE"
    elif pressure <= 0.4:
        return "IRRITATED"
    elif pressure <= 0.6:
        return "HOSTILE"
    elif pressure <= 0.8:
        return "VOLATILE"
    else:
        return "CRITICAL"

def calculate_reclamation_pressure(floor_id, claims, debug=False):
    """
    Calculates the aggregate environmental pushback (Reclamation Pressure).
    """
    # 1. Depth Contribution (0.1 per 3 floors)
    depth_cont = (floor_id // 3) * 0.1
    
    # 2. Visibility Contribution
    # Sum of all claim visibility pressures, scaled by 0.5 to keep in bounds
    total_vis = sum(c.get("visibility_pressure", 0.0) for c in claims)
    vis_cont = min(0.5, total_vis * 0.5)
    
    # 3. Decay Contribution
    # Penalize decaying footholds
    decay_count = sum(1 for c in claims if c.get("status") == "DECAYING")
    decay_cont = min(0.4, decay_count * 0.2)
    
    # Aggregate
    total_press = depth_cont + vis_cont + decay_cont
    total_press = round(max(0.0, min(1.0, total_press)), 4)
    
    # Mutation bias is a direct function of total pressure
    mut_bias = round(total_press * 0.8, 4)
    
    record = {
        "floor_id": floor_id,
        "total_reclamation_pressure": total_press,
        "visibility_contribution": round(vis_cont, 4),
        "decay_contribution": round(decay_cont, 4),
        "depth_contribution": round(depth_cont, 4),
        "reclamation_band": get_reclamation_band(total_press),
        "mutation_risk_bias": mut_bias,
        "bounded_flags_clean": True
    }
    
    _log_debug_event("INFO", "ReclamationCalculated", f"Floor {floor_id} Reclamation: {record['reclamation_band']} ({total_press})", record, debug)
    
    return record

def validate_reclamation_pressure(record, schema_path=None, debug=False):
    """Validates a reclamation pressure record against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _RECLAMATION_SCHEMA_PATH
    return json_save_manager.validate_json(record, schema_path, debug=debug)

def summarize_reclamation_pressure(record):
    """Returns a human-readable summary of the reclamation pressure."""
    if not record:
        return "No reclamation data."
    
    summary = f"Reclamation Status: {record.get('reclamation_band')} ({record.get('total_reclamation_pressure'):.2f}). "
    summary += f"Contributions (Vis:{record.get('visibility_contribution'):.2f}, Decay:{record.get('decay_contribution'):.2f}, Depth:{record.get('depth_contribution'):.2f})."
    return summary
