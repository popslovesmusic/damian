import os
import json
import sys

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import json_save_manager (assuming project root is in sys.path)
# This will also try to import debug_logger internally if available
try:
    from engine.save.runtime import json_save_manager
    _json_save_manager_available = True
except ImportError:
    _json_save_manager_available = False

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
        _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}

def load_state_machine(states_path, transitions_path, debug=False):
    """
    Loads state machine definitions from JSON files.
    Returns structured success with loaded machine or structured error.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)

    states_result = json_save_manager.load_json(states_path, debug=debug)
    if not states_result["ok"]:
        return create_structured_error("LoadStatesError", f"Failed to load states: {states_result['message']}", states_path, debug=debug)
    
    transitions_result = json_save_manager.load_json(transitions_path, debug=debug)
    if not transitions_result["ok"]:
        return create_structured_error("LoadTransitionsError", f"Failed to load transitions: {transitions_result['message']}", transitions_path, debug=debug)
    
    states = {s["state_id"]: s for s in states_result["payload"].get("states", [])}
    transitions = transitions_result["payload"].get("transitions", [])

    machine = {"states": states, "transitions": transitions}
    _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "INFO", "StateMachineLoaded", "State machine loaded successfully.", {"states_path": states_path, "transitions_path": transitions_path}, debug)
    return create_structured_success(machine, debug=debug)

def create_runtime_context(initial_state="BOOT_ENGINE"):
    """
    Creates an initial runtime context for the state machine.
    """
    return {
        "ok": True,
        "current_state": initial_state,
        "visited_states": [initial_state],
        "last_error": None
    }

def can_transition(machine, from_state, to_state):
    """
    Checks if a transition from from_state to to_state is valid.
    """
    for t_from, t_to in machine["transitions"]:
        if t_from == from_state and t_to == to_state:
            return True
    return False

def step_transition(machine, context, to_state, debug=False):
    """
    Attempts to transition the state machine to a new state.
    Updates context and returns structured success or error.
    """
    if not context["ok"]:
        _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "WARNING", "InvalidContext", "Attempted transition on invalid context.", {"context": context}, debug)
        return create_structured_error("InvalidContext", "Cannot transition from an invalid context.", debug=debug)

    from_state = context["current_state"]

    if not machine["states"].get(to_state):
        return create_structured_error("InvalidState", f"Target state '{to_state}' not found in state machine.", debug=debug)
    
    if not can_transition(machine, from_state, to_state):
        _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "ERROR", "InvalidTransition", f"Invalid transition from '{from_state}' to '{to_state}'.", {"from": from_state, "to": to_state}, debug)
        return create_structured_error("InvalidTransition", f"Cannot transition from '{from_state}' to '{to_state}'.", debug=debug)

    context["current_state"] = to_state
    context["visited_states"].append(to_state)
    context["last_error"] = None
    _log_debug_event("TOWER-ENGINE-018", "state_machine_driver", "INFO", "StateTransition", f"Transitioned from '{from_state}' to '{to_state}'.", {"from": from_state, "to": to_state}, debug)
    return create_structured_success(context, debug=debug)

def run_scripted_path(machine, context, path, debug=False):
    """
    Runs a series of transitions defined in a path.
    Returns the final context or structured error.
    """
    for next_state in path:
        result = step_transition(machine, context, next_state, debug=debug)
        if not result["ok"]:
            context["ok"] = False
            context["last_error"] = result
            return create_structured_error(result["error_type"], result["message"], debug=debug)
    return create_structured_success(context, debug=debug)