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
# (We might need a schema for scarring records later, but for now we define the shape here)

PATCH_ID = "TOWER-ENGINE-125"
SYSTEM_NAME = "mutation_scarring_stub"

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

def calculate_localized_scarring(node_id, claims, floor_id, base_residue=0.0, debug=False):
    """
    Calculates deterministic localized scarring pressure for a node.
    """
    # 1. Identify claim on this node
    target_claim = next((c for c in claims if c.get("claim_node_id") == node_id), None)
    
    visibility = 0.0
    decay_bonus = 0.0
    duration_factor = 0.1 # Baseline stress of existence
    
    if target_claim:
        visibility = target_claim.get("visibility_pressure", 0.0)
        if target_claim.get("status") == "DECAYING":
            decay_bonus = 0.2
        elif target_claim.get("status") == "OVERRUN":
            decay_bonus = 0.4
            
    # 2. Depth Contribution
    depth_factor = (floor_id // 3) * 0.05
    
    # Aggregate Scarring Intensity
    # Order strained by existence (duration_factor) + visible attention + instability (decay)
    intensity = duration_factor + (visibility * 0.5) + decay_bonus + depth_factor + (base_residue * 0.2)
    intensity = round(max(0.0, min(1.0, float(intensity))), 4)
    
    # 3. Hazard Bias
    # Higher scarring increases tactical hazard
    hazard_bias = round(intensity * 0.6, 4)
    
    record = {
        "node_id": node_id,
        "floor_id": floor_id,
        "scar_intensity": intensity,
        "hazard_bias": hazard_bias,
        "contributions": {
            "visibility": round(visibility * 0.5, 4),
            "decay": decay_bonus,
            "depth": round(depth_factor, 4),
            "base_residue": round(base_residue * 0.2, 4)
        },
        "bounded_flags_clean": True
    }
    
    _log_debug_event("INFO", "ScarringCalculated", f"Node {node_id} Scar Intensity: {intensity}", record, debug)
    
    return record

def summarize_scarring(record):
    """Returns a human-readable summary of the scarring status."""
    if not record:
        return "No scarring data."
    
    intensity = record.get("scar_intensity", 0.0)
    summary = f"Node {record.get('node_id')} Scarring: {intensity:.2f}. "
    summary += f"Hazard Bias: +{record.get('hazard_bias'):.2f}."
    return summary
