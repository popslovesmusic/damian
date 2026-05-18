import os
import json
import datetime
import uuid
import sys
import random

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
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_SURVIVOR_MARK_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/easter_eggs/contracts/survivor_mark.schema.json")
_FLOOR_MEMORY_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
_SURVIVOR_MARK_REGISTRY_PATH = os.path.join(_PROJECT_ROOT, "engine/easter_eggs/registry/survivor_mark_registry.json")


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
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def _load_survivor_mark_registry(debug=False):
    """Loads the survivor mark registry for default values."""
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    registry_result = json_save_manager.load_json(_SURVIVOR_MARK_REGISTRY_PATH, debug=debug)
    if not registry_result["ok"]:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "ERROR", "RegistryLoadFailure", f"Failed to load survivor mark registry: {registry_result['message']}", debug_enabled=debug)
        return create_structured_error("RegistryLoadFailure", f"Failed to load survivor mark registry: {registry_result['message']}", debug=debug)
    return registry_result


def make_survivor_mark(floor_id, source_mutation_event_id='unknown_mutation', mark_index=1, debug=False):
    """
    Creates a minimal survivor mark record.
    """
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "MakeSurvivorMark", f"Creating survivor mark for floor_id: {floor_id}", {"floor_id": floor_id, "mark_index": mark_index}, debug)

    if not isinstance(floor_id, int) or floor_id < 1:
        return create_structured_error("InvalidInput", f"floor_id must be an integer >= 1, got {floor_id}", debug=debug)
    
    registry_result = _load_survivor_mark_registry(debug=debug)
    if not registry_result["ok"]:
        return create_structured_error("RegistryError", registry_result["message"], debug=debug)
    registry = registry_result["payload"]

    # Use default values from requirements/registry for simplicity
    mark_class_id = registry["mark_classes"][0]["mark_class_id"] if registry["mark_classes"] else "visual_glyph"
    hint_modes = registry["mark_classes"][0]["discoverability_modes"] if registry["mark_classes"] and registry["mark_classes"][0].get("discoverability_modes") else ["visual_hint"]
    reward_class_id = registry["reward_classes"][0]["reward_class_id"] if registry["reward_classes"] else "minor_cache"

    survivor_mark = {
        "survivor_mark_id": f"mark_{floor_id}_{mark_index}_{uuid.uuid4().hex[:8]}",
        "floor_id": floor_id,
        "source_mutation_event_id": source_mutation_event_id,
        "mark_class_id": mark_class_id,
        "hint_modes": hint_modes,
        "placement_context": f"Generated for floor {floor_id} mutation.",
        "claim_condition": "player_interacts_with_mark_after_revealing_hint",
        "reward_class_id": reward_class_id,
        "reward_payload_ref": "mvp_reward_placeholder",
        "is_optional": True,
        "is_discoverable": True,
        "claimed": False,
        "can_mutate_if_unclaimed": True,
        "progression_break_risk": "LOW"
    }

    # Validate the generated mark against its schema
    if not _json_save_manager_available:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "WARNING", "NoJsonSaveManager", "json_save_manager not available, skipping survivor mark schema validation.", debug_enabled=debug)
    else:
        validation_result = json_save_manager.validate_json(survivor_mark, _SURVIVOR_MARK_SCHEMA_PATH, debug=debug)
        if not validation_result["ok"]:
            _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "ERROR", "SurvivorMarkValidationFailure", f"Created survivor mark failed schema validation: {validation_result['message']}", {"mark": survivor_mark, "error": validation_result}, debug)
            return create_structured_error("SurvivorMarkValidationFailure", f"Created survivor mark failed schema validation: {validation_result['message']}", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "DEBUG", "SurvivorMarkCreated", "Survivor mark created successfully.", {"mark": survivor_mark}, debug)
    return create_structured_success(survivor_mark, debug=debug)


def attach_survivor_mark_to_floor_memory(floor_memory, survivor_mark, debug=False):
    """
    Attaches a survivor mark to the unclaimed_easter_eggs list of a floor_memory.
    """
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "AttachSurvivorMark", f"Attaching mark {survivor_mark.get('survivor_mark_id')} to floor {floor_memory.get('floor_id')}.", debug_enabled=debug)

    if not isinstance(floor_memory, dict) or "unclaimed_easter_eggs" not in floor_memory:
        return create_structured_error("InvalidFloorMemory", "Floor memory is invalid or missing 'unclaimed_easter_eggs'.", debug=debug)
    if not isinstance(survivor_mark, dict) or "survivor_mark_id" not in survivor_mark:
        return create_structured_error("InvalidSurvivorMark", "Survivor mark is invalid or missing 'survivor_mark_id'.", debug=debug)

    if survivor_mark["survivor_mark_id"] in floor_memory["unclaimed_easter_eggs"]:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "WARNING", "DuplicateMark", "Survivor mark already attached.", debug_enabled=debug)
        return create_structured_success(floor_memory, debug=debug) # Already there, consider it success

    floor_memory["unclaimed_easter_eggs"].append(survivor_mark["survivor_mark_id"])
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "DEBUG", "MarkAttached", "Survivor mark attached to floor memory.", debug_enabled=debug)
    return create_structured_success(floor_memory, debug=debug)


def discover_survivor_mark(floor_memory, survivor_mark_id, debug=False):
    """
    Simulates discovery of a survivor mark. Moves it from unclaimed to discovered.
    """
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "DiscoverMark", f"Attempting to discover mark {survivor_mark_id} on floor {floor_memory.get('floor_id')}.", debug_enabled=debug)
    if not isinstance(floor_memory, dict) or "unclaimed_easter_eggs" not in floor_memory or "discovered_easter_eggs" not in floor_memory:
        return create_structured_error("InvalidFloorMemory", "Floor memory is invalid or missing easter egg lists.", debug=debug)

    if survivor_mark_id not in floor_memory["unclaimed_easter_eggs"]:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "WARNING", "MarkNotFound", "Survivor mark not found in unclaimed list.", debug_enabled=debug)
        return create_structured_error("MarkNotFound", f"Survivor mark {survivor_mark_id} not found in unclaimed list.", debug=debug)

    floor_memory["unclaimed_easter_eggs"].remove(survivor_mark_id)
    floor_memory["discovered_easter_eggs"].append(survivor_mark_id)
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "MarkDiscovered", f"Survivor mark {survivor_mark_id} moved to discovered.", debug_enabled=debug)
    return create_structured_success(floor_memory, debug=debug)


def claim_survivor_mark(floor_memory, survivor_mark_id, debug=False):
    """
    Simulates claiming a discovered survivor mark. Returns a bounded reward placeholder.
    """
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "ClaimMark", f"Attempting to claim mark {survivor_mark_id} on floor {floor_memory.get('floor_id')}.", debug_enabled=debug)

    if not isinstance(floor_memory, dict) or "discovered_easter_eggs" not in floor_memory:
        return create_structured_error("InvalidFloorMemory", "Floor memory is invalid or missing 'discovered_easter_eggs'.", debug=debug)
    
    # Check if already claimed or not discovered
    if survivor_mark_id not in floor_memory["discovered_easter_eggs"]:
        _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "WARNING", "MarkNotDiscovered", "Survivor mark not in discovered list.", debug_enabled=debug)
        return create_structured_error("MarkNotDiscovered", f"Survivor mark {survivor_mark_id} not in discovered list or already claimed.", debug=debug)

    # For MVP, a simple reward placeholder
    reward_placeholder = {
        "reward_id": f"reward_{survivor_mark_id}",
        "type": "rare_cache",
        "value": random.randint(500, 1500), # Bounded value
        "notes": "MVP placeholder reward."
    }
    
    floor_memory["discovered_easter_eggs"].remove(survivor_mark_id) # Mark as claimed for simplicity
    _log_debug_event("TOWER-ENGINE-029", "mvp_survivor_mark_system", "INFO", "MarkClaimed", f"Survivor mark {survivor_mark_id} claimed. Reward granted.", {"reward": reward_placeholder}, debug_enabled=debug)
    return create_structured_success(reward_placeholder, debug=debug)


def list_unclaimed_survivor_marks(floor_memory):
    """
    Lists unclaimed survivor marks in a floor memory.
    """
    if not isinstance(floor_memory, dict) or "unclaimed_easter_eggs" not in floor_memory:
        return create_structured_error("InvalidFloorMemory", "Floor memory is invalid or missing 'unclaimed_easter_eggs'.")
    
    return create_structured_success(floor_memory["unclaimed_easter_eggs"])
