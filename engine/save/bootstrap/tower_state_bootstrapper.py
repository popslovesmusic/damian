import os
import json
import datetime
import uuid
import sys

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import json_save_manager (assuming project root is in sys.path)
try:
    from engine.save.runtime import json_save_manager
    _json_save_manager_available = True
except ImportError:
    _json_save_manager_available = False

# Paths to existing schemas
# Assume these paths are relative to the project root (D:\projects\Damian)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_TOWER_STATE_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/tower_state.schema.json")
_PLAYER_PROGRESSION_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/player/contracts/player_progression_state.schema.json")
_DOMAIN_STATE_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/domain/contracts/domain_state.schema.json")


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
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_default_tower_state(content_pack_id='damian', engine_version='0.0.1'):
    """
    Creates a default, minimal valid tower state.
    """
    default_state = {
        "tower_state_id": f"tower_state_default_{uuid.uuid4()}",
        "engine_version": engine_version,
        "content_pack_id": content_pack_id,
        "current_floor": 1,
        "highest_floor_reached": 1,
        "total_runs": 0,
        "total_deaths": 0,
        "last_outcome": "BOOTSTRAP",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "global_residue": {},
        "floor_memory": []
    }
    return default_state

def load_tower_state(save_path, schema_path=_TOWER_STATE_SCHEMA_PATH, debug=False):
    """
    Loads a tower state from a file and validates it.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "DEBUG", "LoadAttempt", f"Attempting to load tower state from {save_path}.", {"path": save_path}, debug)
    result = json_save_manager.load_validated_json(save_path, schema_path, debug=debug)
    
    if result["ok"]:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "LoadSuccess", f"Successfully loaded and validated tower state from {save_path}.", {"path": save_path}, debug)
        return create_structured_success(result["payload"], save_path, debug=debug)
    else:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "ERROR", "LoadFailure", f"Failed to load or validate tower state from {save_path}: {result['message']}", {"path": save_path, "error": result}, debug)
        return result # Return the structured error from json_save_manager

def save_tower_state(save_path, tower_state, schema_path=_TOWER_STATE_SCHEMA_PATH, debug=False):
    """
    Saves a tower state to a file after validating it.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "DEBUG", "SaveAttempt", f"Attempting to save tower state to {save_path}.", {"path": save_path}, debug)
    result = json_save_manager.save_validated_json(save_path, tower_state, schema_path, debug=debug)

    if result["ok"]:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "SaveSuccess", f"Successfully saved and validated tower state to {save_path}.", {"path": save_path}, debug)
        return create_structured_success(None, save_path, debug=debug)
    else:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "ERROR", "SaveFailure", f"Failed to save or validate tower state to {save_path}: {result['message']}", {"path": save_path, "error": result}, debug)
        return result # Return the structured error from json_save_manager

def bootstrap_tower_state(save_path, schema_path=_TOWER_STATE_SCHEMA_PATH, create_if_missing=True, debug=False):
    """
    Bootstraps a tower state: loads from save_path if exists and valid,
    otherwise creates a default state (if create_if_missing is True) or errors.
    """
    _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "BootstrapStart", f"Bootstrapping tower state for {save_path}.", {"save_path": save_path, "create_if_missing": create_if_missing}, debug)

    load_result = load_tower_state(save_path, schema_path, debug=debug)

    if load_result["ok"]:
        _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "BootstrapLoadSuccess", "Successfully loaded existing tower state.", {"path": save_path}, debug)
        return load_result
    else:
        if load_result["error_type"] == "FileNotFound" and create_if_missing:
            _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "CreateDefault", f"Save file not found, creating default tower state for {save_path}.", {"path": save_path}, debug)
            default_state = make_default_tower_state()
            save_result = save_tower_state(save_path, default_state, schema_path, debug=debug)
            if save_result["ok"]:
                _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "INFO", "DefaultSaveSuccess", f"Successfully created and saved default tower state to {save_path}.", {"path": save_path}, debug)
                return create_structured_success(default_state, save_path, debug=debug)
            else:
                _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "CRITICAL", "DefaultSaveFailure", f"Failed to save default tower state to {save_path}: {save_result['message']}", {"path": save_path, "error": save_result}, debug)
                return create_structured_error("DefaultSaveError", f"Could not create and save default tower state: {save_result['message']}", save_path, debug=debug)
        elif load_result["error_type"] != "FileNotFound":
            _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "ERROR", "BootstrapLoadFailure", f"Failed to load existing tower state (not FileNotFoundError): {load_result['message']}", {"path": save_path, "error": load_result}, debug)
            return load_result
        else:
            _log_debug_event("TOWER-ENGINE-019", "tower_state_bootstrapper", "WARNING", "BootstrapNoCreate", f"Save file not found and create_if_missing is False for {save_path}.", {"path": save_path}, debug)
            return load_result # File not found and not creating, return file not found error
