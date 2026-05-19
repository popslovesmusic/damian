import os
import json
import sys
import datetime

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False


def _log_debug_event(patch_id, system, severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        event = debug_logger.make_debug_event(patch_id, system, severity, event_type, message, context)
        # Assuming debug_logger.write_debug_event handles its own failures
        debug_logger.write_debug_event(event)
    elif not _debug_logger_available and debug_enabled:
        print(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: {message}")


def create_structured_error(error_type, message, path="", debug=False):
    """Creates a structured error dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-008", "mvp_floor_progression", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-008", "mvp_floor_progression", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def validate_mvp_floor_bounds(tower_state, max_floor=100, debug=False):
    """
    Validates if the current floor in tower_state is within bounds.
    """
    current_floor = tower_state.get("current_floor")
    if current_floor is None:
        return create_structured_error("InvalidTowerState", "current_floor missing in tower_state.", debug=debug)
    
    if current_floor < 1 or current_floor > max_floor:
        return create_structured_error("FloorOutOfBounds", f"Floor {current_floor} is out of bounds (1-{max_floor}).", debug=debug)
    
    return {"ok": True}


def apply_victory_ascend(tower_state, max_floor=100, debug=False):
    """
    Increments current floor upon victory, up to max_floor.
    """
    _log_debug_event("TOWER-ENGINE-008", "mvp_floor_progression", "INFO", "VictoryAscend", "Applying victory ascend.", debug_enabled=debug)

    bounds_check = validate_mvp_floor_bounds(tower_state, max_floor, debug=debug)
    if not bounds_check["ok"]:
        return bounds_check

    current_floor = tower_state["current_floor"]
    floor_changed = False
    
    if current_floor < max_floor:
        tower_state["current_floor"] += 1
        floor_changed = True
        if tower_state["current_floor"] > tower_state.get("highest_floor_reached", 0):
            tower_state["highest_floor_reached"] = tower_state["current_floor"]
    
    tower_state["last_outcome"] = "VICTORY_ASCEND"
    tower_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return {"ok": True, "tower_state": tower_state, "floor_changed": floor_changed}


def apply_defeat_drop(tower_state, min_floor=1, debug=False):
    """
    Decrements current floor upon defeat, down to min_floor.
    """
    _log_debug_event("TOWER-ENGINE-008", "mvp_floor_progression", "INFO", "DefeatDrop", "Applying defeat drop.", debug_enabled=debug)

    current_floor = tower_state.get("current_floor")
    if current_floor is None:
        return create_structured_error("InvalidTowerState", "current_floor missing in tower_state.", debug=debug)

    floor_changed = False
    if current_floor > min_floor:
        tower_state["current_floor"] -= 1
        floor_changed = True
    
    tower_state["last_outcome"] = "DEFEAT_DROP"
    tower_state["total_deaths"] = tower_state.get("total_deaths", 0) + 1
    tower_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return {"ok": True, "tower_state": tower_state, "floor_changed": floor_changed}


def resolve_floor_outcome(tower_state, outcome, debug=False):
    """
    Orchestrates floor progression based on outcome.
    """
    if not isinstance(tower_state, dict) or "current_floor" not in tower_state:
        return {"ok": False, "error": {"error_type": "InvalidTowerState", "message": "Invalid tower state."}}

    if outcome == "VICTORY_ASCEND":
        result = apply_victory_ascend(tower_state, debug=debug)
        if result["ok"]:
            return {"ok": True, "outcome": "VICTORY_ASCEND", "tower_state": result["tower_state"], "floor_changed": result["floor_changed"]}
        return {"ok": False, "error": result}

    elif outcome == "DEFEAT_DROP":
        result = apply_defeat_drop(tower_state, debug=debug)
        if result["ok"]:
            return {"ok": True, "outcome": "DEFEAT_DROP", "tower_state": result["tower_state"], "floor_changed": result["floor_changed"]}
        return {"ok": False, "error": result}

    elif outcome == "RETREAT_TO_HUB":
        tower_state["last_outcome"] = "RETREAT_TO_HUB"
        tower_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"ok": True, "outcome": "RETREAT_TO_HUB", "tower_state": tower_state, "floor_changed": False}

    elif outcome == "EXIT_GAME":
        tower_state["last_outcome"] = "EXIT_GAME"
        tower_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {"ok": True, "outcome": "EXIT_GAME", "tower_state": tower_state, "shutdown_requested": True}

    else:
        return {"ok": False, "error": {"error_type": "InvalidOutcome", "message": f"Unsupported outcome: {outcome}"}}


def can_enter_floor(tower_state, target_floor, max_floor=100, debug=False):
    """
    Checks if the player can enter the target floor.
    """
    if target_floor < 1 or target_floor > max_floor:
        return create_structured_error("FloorOutOfBounds", f"Floor {target_floor} is out of bounds.", debug=debug)
    
    highest_reached = tower_state.get("highest_floor_reached", 1)
    if target_floor > highest_reached:
        return create_structured_error("FloorLocked", f"Floor {target_floor} is locked.", debug=debug)
    
    return {"ok": True}
