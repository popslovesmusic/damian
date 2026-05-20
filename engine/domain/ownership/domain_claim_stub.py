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
_CLAIM_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/domain/ownership/contracts/domain_claim.schema.json")

PATCH_ID = "TOWER-ENGINE-110"
SYSTEM_NAME = "domain_claim_stub"

CLAIM_TYPE_BEHAVIOR = {
    "recovery_anchor": {
        "recovery_value_bias": 0.20,
        "maintenance_pressure_bias": 0.10,
        "visibility_pressure_bias": 0.10
    },
    "supply_cache": {
        "recovery_value_bias": 0.10,
        "maintenance_pressure_bias": 0.15,
        "visibility_pressure_bias": 0.18
    },
    "repair_station": {
        "recovery_value_bias": 0.15,
        "maintenance_pressure_bias": 0.22,
        "visibility_pressure_bias": 0.20
    },
    "survivor_outpost": {
        "recovery_value_bias": 0.18,
        "maintenance_pressure_bias": 0.25,
        "visibility_pressure_bias": 0.28
    },
    "observation_post": {
        "recovery_value_bias": 0.05,
        "maintenance_pressure_bias": 0.12,
        "visibility_pressure_bias": 0.24
    }
}

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

def calculate_domain_claim_pressure(claim_type, floor_id, residue_strength=0.0, debug=False):
    """
    Calculates deterministic bounded pressures for a domain claim.
    """
    if claim_type not in CLAIM_TYPE_BEHAVIOR:
        return None

    behavior = CLAIM_TYPE_BEHAVIOR[claim_type]
    
    # Scale base pressures with floor depth
    # Higher floor_id increases maintenance and visibility pressure
    floor_factor = (int(floor_id) - 1) * 0.05
    
    m_press = behavior["maintenance_pressure_bias"] + floor_factor
    v_press = behavior["visibility_pressure_bias"] + floor_factor
    rec_val = behavior["recovery_value_bias"]
    
    # Mutation threat scales with residue strength
    mut_threat = (float(residue_strength) * 0.5) + (floor_factor * 0.3)

    # Clamp results
    return {
        "maintenance_pressure": round(max(0.0, min(1.0, float(m_press))), 4),
        "visibility_pressure": round(max(0.0, min(1.0, float(v_press))), 4),
        "recovery_value": round(max(0.0, min(1.0, float(rec_val))), 4),
        "mutation_threat": round(max(0.0, min(1.0, float(mut_threat))), 4),
        "residue_strength": round(max(0.0, min(1.0, float(residue_strength))), 4)
    }

def make_domain_claim(player_id, floor_id, claim_node_id, claim_type='recovery_anchor', debug=False):
    """
    Creates a schema-compatible DomainClaim record.
    """
    if claim_type not in CLAIM_TYPE_BEHAVIOR:
        _log_debug_event("ERROR", "InvalidClaimType", f"Invalid claim type: {claim_type}", debug_enabled=debug)
        return {"ok": False, "error": "InvalidClaimType", "message": f"Claim type must be one of {list(CLAIM_TYPE_BEHAVIOR.keys())}"}

    try:
        f_id = int(floor_id)
        if f_id < 0:
            raise ValueError("Floor ID must be non-negative")
    except (ValueError, TypeError):
        return {"ok": False, "error": "InvalidFloorID", "message": "Floor ID must be a non-negative integer."}

    # Derive pressures (using 0.1 baseline residue for new claim)
    pressures = calculate_domain_claim_pressure(claim_type, f_id, residue_strength=0.1, debug=debug)
    
    claim = {
        "claim_id": f"claim_{uuid.uuid4()}",
        "player_id": str(player_id),
        "floor_id": f_id,
        "claim_node_id": str(claim_node_id),
        "claim_type": claim_type,
        "status": "ACTIVE",
        "maintenance_pressure": pressures["maintenance_pressure"],
        "visibility_pressure": pressures["visibility_pressure"],
        "recovery_value": pressures["recovery_value"],
        "mutation_threat": pressures["mutation_threat"],
        "residue_strength": pressures["residue_strength"],
        "recoverability_supported": True,
        "tower_hostility_preserved": True,
        "bounded_flags_clean": True
    }

    _log_debug_event("INFO", "ClaimCreated", f"Domain claim created: {claim_type} at {claim_node_id}", {"claim_id": claim["claim_id"]}, debug)
    
    return {
        "ok": True,
        "domain_claim": claim,
        "summary": summarize_domain_claim(claim),
        "error": None
    }

def validate_domain_claim(domain_claim, schema_path=None, debug=False):
    """Validates a domain claim record against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _CLAIM_SCHEMA_PATH
    return json_save_manager.validate_json(domain_claim, schema_path, debug=debug)

def summarize_domain_claim(domain_claim):
    """Returns a human-readable summary of the domain claim."""
    if not domain_claim:
        return "No domain claim."
    
    summary = f"Domain Claim ({domain_claim.get('claim_type')}): "
    summary += f"Floor {domain_claim.get('floor_id')}, Node {domain_claim.get('claim_node_id')}. "
    summary += f"Pressure (Maint:{domain_claim.get('maintenance_pressure'):.2f}, Vis:{domain_claim.get('visibility_pressure'):.2f}). "
    summary += f"Recovery: {domain_claim.get('recovery_value'):.2f}."
    return summary
