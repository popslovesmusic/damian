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
_PLAYER_PROGRESSION_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/player/contracts/player_progression_state.schema.json")


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
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_default_player_progression(player_id='player_default_001', profile_id='profile_default_001', content_pack_id='damian'):
    """
    Creates a default, minimal valid player progression state.
    """
    default_progression = {
        "player_id": f"{player_id}_{uuid.uuid4().hex[:8]}",
        "profile_id": f"{profile_id}_{uuid.uuid4().hex[:8]}",
        "content_pack_id": content_pack_id,
        "level": 1,
        "highest_floor_reached": 1,
        "active_orientation": "unbound",
        "stats": {
            "health": 100.0,
            "damage": 10.0,
            "defense": 0.0,
            "speed": 1.0,
            "recovery": 0.0
        },
        "unlocked_skills": [],
        "equipped_items": [],
        "residue_pressure": {
            "dominant_build_visibility": 0.0,
            "power_use_strain": 0.0,
            "overoptimization_pressure": 0.0
        },
        "forbidden_flags": {
            "permanent_invulnerability": False,
            "infinite_damage_scaling": False,
            "residue_immunity": False,
            "death_consequence_immunity": False
        }
    }
    return default_progression

def load_player_progression(save_path, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, debug=False):
    """
    Loads a player progression state from a file and validates it.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "DEBUG", "LoadAttempt", f"Attempting to load player progression from {save_path}.", {"path": save_path}, debug)
    result = json_save_manager.load_validated_json(save_path, schema_path, debug=debug)
    
    if result["ok"]:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "LoadSuccess", f"Successfully loaded and validated player progression from {save_path}.", {"path": save_path}, debug)
        return create_structured_success(result["payload"], save_path, debug=debug)
    else:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "ERROR", "LoadFailure", f"Failed to load or validate player progression from {save_path}: {result['message']}", {"path": save_path, "error": result}, debug)
        return result # Return the structured error from json_save_manager

def save_player_progression(save_path, player_progression, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, debug=False):
    """
    Saves a player progression state to a file after validating it.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "DEBUG", "SaveAttempt", f"Attempting to save player progression to {save_path}.", {"path": save_path}, debug)
    result = json_save_manager.save_validated_json(save_path, player_progression, schema_path, debug=debug)

    if result["ok"]:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "SaveSuccess", f"Successfully saved and validated player progression to {save_path}.", {"path": save_path}, debug)
        return create_structured_success(None, save_path, debug=debug)
    else:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "ERROR", "SaveFailure", f"Failed to save or validate player progression to {save_path}: {result['message']}", {"path": save_path, "error": result}, debug)
        return result # Return the structured error from json_save_manager

def bootstrap_player_progression(save_path, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, create_if_missing=True, debug=False):
    """
    Bootstraps a player progression state: loads from save_path if exists and valid,
    otherwise creates a default state (if create_if_missing is True) or errors.
    """
    _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "BootstrapStart", f"Bootstrapping player progression for {save_path}.", {"save_path": save_path, "create_if_missing": create_if_missing}, debug)

    load_result = load_player_progression(save_path, schema_path, debug=debug)

    if load_result["ok"]:
        _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "BootstrapLoadSuccess", "Successfully loaded existing player progression.", {"path": save_path}, debug)
        return load_result
    else:
        if load_result["error_type"] == "FileNotFound" and create_if_missing:
            _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "CreateDefault", f"Save file not found, creating default player progression for {save_path}.", {"path": save_path}, debug)
            default_progression = make_default_player_progression()
            save_result = save_player_progression(save_path, default_progression, schema_path, debug=debug)
            if save_result["ok"]:
                _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "INFO", "DefaultSaveSuccess", f"Successfully created and saved default player progression to {save_path}.", {"path": save_path}, debug)
                return create_structured_success(default_progression, save_path, debug=debug)
            else:
                _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "CRITICAL", "DefaultSaveFailure", f"Failed to save default player progression to {save_path}: {save_result['message']}", {"path": save_path, "error": save_result}, debug)
                return create_structured_error("DefaultSaveError", f"Could not create and save default player progression: {save_result['message']}", save_path, debug=debug)
        elif load_result["error_type"] != "FileNotFound":
            _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "ERROR", "BootstrapLoadFailure", f"Failed to load existing player progression (not FileNotFoundError): {load_result['message']}", {"path": save_path, "error": load_result}, debug)
            return load_result
        else:
            _log_debug_event("TOWER-ENGINE-020", "player_progression_bootstrapper", "WARNING", "BootstrapNoCreate", f"Save file not found and create_if_missing is False for {save_path}.", {"path": save_path}, debug)
            return load_result # File not found and not creating, return file not found error