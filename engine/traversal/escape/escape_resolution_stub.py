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

# Import MVP systems
try:
    from engine.prototype.runtime import mvp_outcome_pipeline
    from engine.save.runtime import json_save_manager
    _dependencies_available = True
except ImportError:
    _dependencies_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_ESCAPE_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/traversal/escape/contracts/escape_resolution.schema.json")

PATCH_ID = "TOWER-ENGINE-100"
SYSTEM_NAME = "escape_resolution_stub"

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

def resolve_escape_attempt(player_id, floor_id, escape_risk=0.0, route_exposure=0.0, escape_modifier=0.0, source_route_id=None, debug=False):
    """
    Deterministic resolution of an escape attempt based on risk and exposure.
    """
    risk = max(0.0, min(1.0, float(escape_risk)))
    exposure = max(0.0, min(1.0, float(route_exposure)))
    modifier = max(-1.0, min(1.0, float(escape_modifier)))

    # Determine outcome based on risk thresholds (TOWER-ENGINE-100)
    if risk <= 0.30:
        outcome = "ESCAPE_SUCCESS"
        pipeline_outcome = "RETREAT_TO_HUB"
    elif risk <= 0.60:
        outcome = "ESCAPE_PARTIAL"
        pipeline_outcome = "RETREAT_TO_HUB"
    elif risk <= 0.80:
        outcome = "ESCAPE_FAILED_PRESSURE_SPIKE"
        pipeline_outcome = "RETREAT_TO_HUB"
    elif risk > 0.80 and exposure >= 0.70:
        outcome = "ESCAPE_FAILED_RETREAT_DROP"
        pipeline_outcome = "DEFEAT_DROP"
    else:
        # High risk but moderate exposure
        outcome = "ESCAPE_FAILED_RESOURCE_LOSS"
        pipeline_outcome = "RETREAT_TO_HUB"

    # Consequences
    mutation_delta = 0.0
    res_loss = {"gold": 0.0, "potions": 0, "repair_materials": 0}

    if outcome == "ESCAPE_PARTIAL":
        res_loss["gold"] = 100.0
    elif outcome == "ESCAPE_FAILED_PRESSURE_SPIKE":
        mutation_delta = 0.1
        res_loss["gold"] = 250.0
    elif outcome == "ESCAPE_FAILED_RESOURCE_LOSS":
        res_loss["gold"] = 500.0
        res_loss["potions"] = 2
    elif outcome == "ESCAPE_FAILED_RETREAT_DROP":
        mutation_delta = 0.2
        res_loss["gold"] = 1000.0
        res_loss["potions"] = 5
        res_loss["repair_materials"] = 2

    resolution = {
        "escape_resolution_id": f"escape_res_{uuid.uuid4()}",
        "player_id": player_id,
        "floor_id": int(floor_id),
        "source_route_id": source_route_id,
        "escape_risk": risk,
        "route_exposure": exposure,
        "escape_modifier": modifier,
        "outcome": outcome,
        "pipeline_outcome": pipeline_outcome,
        "residue_written": True, # All resolutions write residue (TOWER-ENGINE-100)
        "mutation_pressure_delta": mutation_delta,
        "resource_loss": res_loss,
        "recoverability_preserved": True,
        "floor_identity_preserved": True,
        "bounded_flags_clean": True
    }

    _log_debug_event("INFO", "EscapeResolved", f"Resolved escape: {outcome} ({pipeline_outcome})", {"risk": risk}, debug)
    
    return {
        "ok": True,
        "escape_resolution": resolution,
        "summary": summarize_escape_resolution(resolution),
        "error": None
    }

def resolve_escape_into_pipeline(tower_state, escape_resolution, debug=False):
    """
    Executes the escape consequences through the MVP outcome pipeline.
    """
    if not _dependencies_available:
        return {"ok": False, "error": "Outcome pipeline not available."}

    pipeline_outcome = escape_resolution["pipeline_outcome"]
    
    # Map NONE to something safe if it ever occurs (though not in resolve_escape_attempt)
    if pipeline_outcome == "NONE":
         return {"ok": True, "escape_resolution": escape_resolution, "pipeline_result": None, "summary": "No pipeline action needed."}

    pipeline_result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(tower_state, pipeline_outcome, debug=debug)
    
    if not pipeline_result["ok"]:
        return {"ok": False, "error": pipeline_result.get("error"), "message": pipeline_result.get("message")}

    return {
        "ok": True,
        "escape_resolution": escape_resolution,
        "pipeline_result": pipeline_result,
        "summary": summarize_escape_resolution(escape_resolution),
        "error": None
    }

def validate_escape_resolution(escape_resolution, schema_path=None, debug=False):
    """Validates an escape resolution record against its schema."""
    if not _dependencies_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _ESCAPE_SCHEMA_PATH
    return json_save_manager.validate_json(escape_resolution, schema_path, debug=debug)

def summarize_escape_resolution(escape_resolution):
    """Returns a human-readable summary of the escape resolution."""
    if not escape_resolution:
        return "No escape resolution."
    
    outcome = escape_resolution.get("outcome")
    loss = escape_resolution.get("resource_loss", {})
    
    summary = f"Escape Outcome: {outcome}. "
    if outcome == "ESCAPE_SUCCESS":
        summary += "Safe retreat achieved."
    elif outcome == "ESCAPE_PARTIAL":
        summary += f"Retreated, but lost {loss.get('gold')} gold."
    elif outcome == "ESCAPE_FAILED_RETREAT_DROP":
        summary += "Retreat failed! Severe drop incurred."
    else:
        summary += f"Retreat hindered. Mutation pressure +{escape_resolution.get('mutation_pressure_delta')}."
    
    return summary
