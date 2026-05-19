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
_MUTATION_EVENT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/mutation/contracts/floor_mutation_event.schema.json")
_FLOOR_MEMORY_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
_FLOOR_IDENTITY_RULES_PATH = os.path.join(_PROJECT_ROOT, "engine/floor_generation/identity/floor_identity_preservation_rules.json")


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
        _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_stub_mutation_event(floor_id, triggering_residue_id='unknown_residue', debug=False):
    """
    Creates a minimal, deterministic mutation event stub for a DEFEAT_DROP.
    """
    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "MakeMutationEvent", f"Creating stub mutation event for floor_id: {floor_id}", {"floor_id": floor_id, "triggering_residue_id": triggering_residue_id}, debug)

    if not isinstance(floor_id, int) or floor_id < 1:
        return create_structured_error("InvalidInput", f"floor_id must be an integer >= 1, got {floor_id}", debug=debug)
    if not isinstance(triggering_residue_id, str) or not triggering_residue_id:
        return create_structured_error("InvalidInput", "triggering_residue_id cannot be empty.", debug=debug)

    default_stub_mutations = [
      {
        "channel_id": "layout",
        "mutation_id": "minor_corridor_shift_stub",
        "severity": 1,
        "preserves_floor_identity": True,
        "preserves_playability": True
      },
      {
        "channel_id": "easter_eggs",
        "mutation_id": "survivor_mark_opportunity_stub",
        "severity": 1,
        "preserves_floor_identity": True,
        "preserves_playability": True
      },
      {
        "channel_id": "stability",
        "mutation_id": "minor_deviation_increase_stub",
        "severity": 1,
        "preserves_floor_identity": True,
        "preserves_playability": True
      }
    ]

    applied_channels = [m["channel_id"] for m in default_stub_mutations]

    mutation_event = {
        "mutation_event_id": str(uuid.uuid4()),
        "floor_id": floor_id,
        "source_outcome": "DEFEAT_DROP", # As per rules, only for DEFEAT_DROP
        "triggering_residue_id": triggering_residue_id,
        "applied_channels": applied_channels,
        "mutations": default_stub_mutations,
        "floor_identity_preserved": True,
        "playability_preserved": True,
        "mutation_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    # Validate the generated event against its schema
    if not _json_save_manager_available:
        _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "WARNING", "NoJsonSaveManager", "json_save_manager not available, skipping mutation event schema validation.", debug_enabled=debug)
    else:
        validation_result = json_save_manager.validate_json(mutation_event, _MUTATION_EVENT_SCHEMA_PATH, debug=debug)
        if not validation_result["ok"]:
            _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "ERROR", "MutationEventValidationFailure", f"Created mutation event failed schema validation: {validation_result['message']}", {"event": mutation_event, "error": validation_result}, debug)
            return create_structured_error("MutationEventValidationFailure", f"Created mutation event failed schema validation: {validation_result['message']}", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "DEBUG", "MutationEventCreated", "Stub mutation event created successfully.", {"event": mutation_event}, debug)
    return create_structured_success(mutation_event, debug=debug)


def apply_stub_mutation_to_floor_memory(floor_memory, mutation_event, debug=False):
    """
    Applies the effects of a stub mutation event to a floor memory record.
    """
    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "ApplyStubMutation", f"Applying stub mutation to floor {floor_memory.get('floor_id')}.", {"mutation_event_id": mutation_event.get("mutation_event_id")}, debug)

    if not isinstance(floor_memory, dict) or "mutation_level" not in floor_memory:
        return create_structured_error("InvalidFloorMemory", "Invalid floor_memory provided for mutation.", debug=debug)
    if not isinstance(mutation_event, dict) or "mutations" not in mutation_event:
        return create_structured_error("InvalidMutationEvent", "Invalid mutation_event provided.", debug=debug)

    # Increment mutation level
    floor_memory["mutation_level"] = floor_memory.get("mutation_level", 0) + 1
    
    # Add active mutations (if not already present)
    for mutation in mutation_event["mutations"]:
        mutation_id = mutation["mutation_id"]
        if mutation_id not in floor_memory["active_mutations"]:
            floor_memory["active_mutations"].append(mutation_id)

    # Apply stability/deviation changes (simple stub for MVP)
    floor_memory["stability"] = max(0.0, min(1.0, floor_memory.get("stability", 1.0) - random.uniform(0.01, 0.05)))
    floor_memory["deviation"] = max(0.0, min(1.0, floor_memory.get("deviation", 0.0) + random.uniform(0.01, 0.05)))
    
    # Ensure floor memory remains valid against schema
    if not _json_save_manager_available:
        _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "WARNING", "NoJsonSaveManager", "json_save_manager not available, skipping floor memory schema validation after mutation.", debug_enabled=debug)
    else:
        validation_result = json_save_manager.validate_json(floor_memory, _FLOOR_MEMORY_SCHEMA_PATH, debug=debug)
        if not validation_result["ok"]:
            _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "ERROR", "FloorMemoryValidationFailure", f"Mutated floor memory failed schema validation: {validation_result['message']}", {"floor_memory": floor_memory, "error": validation_result}, debug)
            return create_structured_error("FloorMemoryValidationFailure", f"Mutated floor memory failed schema validation: {validation_result['message']}", debug=debug)

    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "StubMutationApplied", "Stub mutation applied to floor memory.", {"floor_memory": floor_memory}, debug)
    return create_structured_success(floor_memory, debug=debug)


def apply_replay_floor_mutation_stub(tower_state, floor_id, triggering_residue_id='unknown_residue', debug=False):
    """
    Coordinates the application of a replay floor mutation stub.
    This should typically be called after a DEFEAT_DROP outcome.
    """
    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "ApplyReplayMutation", f"Applying replay floor mutation stub for floor {floor_id}.", {"floor_id": floor_id, "triggering_residue_id": triggering_residue_id}, debug)

    # 1. Get or create floor memory (using the helper from mvp_residue_writer if available, otherwise minimal)
    try:
        from engine.residue.runtime import mvp_residue_writer
        get_or_create_floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, floor_id, debug=debug)
        if not get_or_create_floor_memory_result["ok"]:
            return create_structured_error("FloorMemoryError", f"Failed to get or create floor memory: {get_or_create_floor_memory_result['message']}", debug=debug)
        floor_memory = get_or_create_floor_memory_result["payload"]
    except ImportError:
        _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "WARNING", "ResidueWriterUnavailable", "mvp_residue_writer not available, using minimal floor memory creation.", debug_enabled=debug)
        # Fallback to manual creation if mvp_residue_writer is not available
        found = False
        for fm in tower_state.get("floor_memory", []):
            if fm.get("floor_id") == floor_id:
                floor_memory = fm
                found = True
                break
        if not found:
            # This minimal version won't load layout_seed properly without floor_record_builder
            floor_memory = {
                "floor_id": floor_id,
                "visit_count": 0, "death_count": 0, "victory_count": 0,
                "stability": 1.0, "deviation": 0.0, "mutation_level": 0,
                "known_layout_seed": f"fallback_seed_{floor_id}",
                "active_mutations": [], "discovered_easter_eggs": [],
                "unclaimed_easter_eggs": [], "residue_history": []
            }
            tower_state.get("floor_memory", []).append(floor_memory) # Ensure floor_memory exists

    # 2. Make stub mutation event
    mutation_event_result = make_stub_mutation_event(floor_id, triggering_residue_id, debug=debug)
    if not mutation_event_result["ok"]:
        return create_structured_error("MutationEventCreationFailure", f"Failed to create mutation event: {mutation_event_result['message']}", debug=debug)
    mutation_event = mutation_event_result["payload"]

    # 3. Apply mutation to floor memory
    apply_result = apply_stub_mutation_to_floor_memory(floor_memory, mutation_event, debug=debug)
    if not apply_result["ok"]:
        return create_structured_error("MutationApplicationFailure", f"Failed to apply mutation to floor memory: {apply_result['message']}", debug=debug)

    _log_debug_event("TOWER-ENGINE-026", "mvp_floor_mutation_stub", "INFO", "ReplayMutationApplied", f"Replay floor mutation stub applied to floor {floor_id}.", {"floor_id": floor_id, "mutation_event": mutation_event}, debug)
    return create_structured_success(tower_state, debug=debug)
