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

# Import inventory systems
try:
    from engine.inventory.runtime import inventory_capacity_pressure
    _capacity_available = True
except ImportError:
    _capacity_available = False

# Import json_save_manager for validation
try:
    from engine.save.runtime import json_save_manager
    _save_manager_available = True
except ImportError:
    _save_manager_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_EVENT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/traversal/runtime/contracts/traversal_event.schema.json")

PATCH_ID = "TOWER-ENGINE-094"
SYSTEM_NAME = "traversal_pressure_stub"

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

def calculate_traversal_pressure(capacity_pressure=0.0, mutation_pressure=0.0, combat_exposure=0.0, repair_burden=0.0, route_exposure=0.0, environmental_profile=None, debug=False):
    """
    Calculates traversal pressure as a bounded weighted combination of factors.
    All inputs are clamped between 0.0 and 1.0.
    """
    # Clamp inputs
    cap_p = max(0.0, min(1.0, float(capacity_pressure)))
    mut_p = max(0.0, min(1.0, float(mutation_pressure)))
    comb_e = max(0.0, min(1.0, float(combat_exposure)))
    rep_b = max(0.0, min(1.0, float(repair_burden)))
    rou_e = max(0.0, min(1.0, float(route_exposure)))

    # Weights (Deterministic balance)
    # Combat exposure and Mutation instability are major factors
    # Capacity and Repair burden are modifiers
    # Route exposure acts as a significant factor in the journey (TOWER-ENGINE-094)
    weights = {
        "combat_exposure": 0.35,
        "mutation_pressure": 0.25,
        "route_exposure": 0.2,
        "capacity_pressure": 0.15,
        "repair_burden": 0.05
    }

    pressure = (
        comb_e * weights["combat_exposure"] +
        mut_p * weights["mutation_pressure"] +
        rou_e * weights["route_exposure"] +
        cap_p * weights["capacity_pressure"] +
        rep_b * weights["repair_burden"]
    )

    # Environmental profile influence (TOWER-ENGINE-094)
    if environmental_profile:
        # Increase pressure based on darkness and instability
        env_bias = (environmental_profile.get("darkness", 0.0) * 0.1) + (environmental_profile.get("instability", 0.0) * 0.1)
        pressure += env_bias

    result = round(max(0.0, min(1.0, pressure)), 4)
    _log_debug_event("INFO", "PressureCalculated", f"Calculated traversal pressure: {result}", {"inputs": [cap_p, mut_p, comb_e, rep_b, rou_e]}, debug)
    return result

def calculate_escape_risk(traversal_pressure, route_exposure=0.0, escape_modifier=0.0, debug=False):
    """
    Calculates escape risk based on traversal pressure, route exposure, and escape modifier.
    Clamped between 0.0 and 1.0.
    """
    tp = max(0.0, min(1.0, float(traversal_pressure)))
    re = max(0.0, min(1.0, float(route_exposure)))
    em = max(-1.0, min(1.0, float(escape_modifier)))

    # Escape is harder when pressure is high or route is exposed
    # For MVP: Weighted toward pressure
    # Escape modifier directly influences risk (positive lowers risk, negative raises it)
    risk = (tp * 0.7) + (re * 0.3) - em
    
    result = round(max(0.0, min(1.0, risk)), 4)
    _log_debug_event("INFO", "RiskCalculated", f"Calculated escape risk: {result}", {"tp": tp, "re": re, "em": em}, debug)
    return result

def make_traversal_event(player_id, source_floor_id, destination_floor_id, traversal_type='advance', pressure_inputs=None, route=None, debug=False):
    """
    Creates a schema-compatible TraversalEvent record.
    """
    if pressure_inputs is None:
        pressure_inputs = {}

    valid_types = ["advance", "retreat", "escape_attempt", "supply_run", "mutation_route"]
    if traversal_type not in valid_types:
        _log_debug_event("ERROR", "InvalidTraversalType", f"Invalid type: {traversal_type}", debug_enabled=debug)
        return {"ok": False, "error": "InvalidTraversalType", "message": f"Type must be one of {valid_types}"}

    # Extract pressures, using inventory_capacity_pressure if state is provided
    cap_p = pressure_inputs.get("capacity_pressure", 0.0)
    if "inventory_state" in pressure_inputs and _capacity_available:
        calc_cap = inventory_capacity_pressure.calculate_capacity_pressure(pressure_inputs["inventory_state"], debug=debug)
        if calc_cap is not None:
            cap_p = calc_cap

    mut_p = pressure_inputs.get("mutation_pressure", 0.0)
    comb_e = pressure_inputs.get("combat_exposure", 0.0)
    rep_b = pressure_inputs.get("repair_burden", 0.0)
    
    # Route evidence integration (TOWER-ENGINE-094)
    route_id = None
    route_type = None
    env_profile = None
    esc_mod = 0.0
    route_e = pressure_inputs.get("route_exposure", 0.0)
    
    if route:
        route_id = route.get("route_id")
        route_type = route.get("route_type")
        env_profile = route.get("environmental_profile")
        esc_mod = route.get("escape_modifier", 0.0)
        route_e = route.get("route_exposure", 0.0)

    tp = calculate_traversal_pressure(cap_p, mut_p, comb_e, rep_b, route_e, env_profile, debug=debug)
    risk = calculate_escape_risk(tp, route_e, esc_mod, debug=debug)

    event = {
        "event_id": f"traversal_{uuid.uuid4()}",
        "player_id": player_id,
        "source_floor_id": str(source_floor_id),
        "destination_floor_id": str(destination_floor_id),
        "traversal_type": traversal_type,
        "traversal_pressure": {
            "capacity_pressure": cap_p,
            "mutation_pressure": mut_p,
            "combat_exposure": comb_e,
            "repair_burden": rep_b,
            "total_pressure": tp # Added for audit trail visibility
        },
        "escape_risk": risk,
        "route_exposure": route_e,
        "route_id": route_id,
        "route_type": route_type,
        "environmental_profile": env_profile,
        "escape_modifier": esc_mod,
        "route_pressure_used": route is not None,
        "bounded_flags_clean": True
    }

    _log_debug_event("INFO", "EventCreated", f"Traversal event created: {traversal_type} {source_floor_id}->{destination_floor_id}", {"event_id": event["event_id"]}, debug)
    
    return {
        "ok": True,
        "traversal_event": event,
        "summary": summarize_traversal_event(event),
        "error": None
    }

def validate_traversal_event(traversal_event, schema_path=None, debug=False):
    """Validates a traversal event against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _EVENT_SCHEMA_PATH
    return json_save_manager.validate_json(traversal_event, schema_path, debug=debug)

def summarize_traversal_event(traversal_event):
    """Returns a human-readable summary of the traversal event."""
    if not traversal_event:
        return "No traversal event."
    
    tp = traversal_event.get("traversal_pressure", {})
    summary = f"Traversal ({traversal_event.get('traversal_type')}): "
    
    if traversal_event.get("route_id"):
        summary += f"Route {traversal_event.get('route_id')} ({traversal_event.get('route_type')}). "
    
    summary += f"{traversal_event.get('source_floor_id')} -> {traversal_event.get('destination_floor_id')}. "
    summary += f"Risk: {traversal_event.get('escape_risk'):.2f}, "
    summary += f"Pressure: {tp.get('total_pressure', 0.0):.2f} (Cap:{tp.get('capacity_pressure', 0.0):.2f}, Mut:{tp.get('mutation_pressure', 0.0):.2f})"
    
    if traversal_event.get("environmental_profile"):
        ep = traversal_event["environmental_profile"]
        summary += f" | Env: Darkness {ep.get('darkness', 0.0):.2f}, Enemy {ep.get('enemy_exposure', 0.0):.2f}"
        
    return summary
