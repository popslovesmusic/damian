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
_RESIDUE_RECORD_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/residue_record.schema.json")
_FLOOR_MEMORY_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")


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
        _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_residue_record(floor_id, outcome, party_size=1, death_event=False, mutation_triggered=False, debug=False):
    """
    Creates a minimal residue record.
    """
    if not isinstance(floor_id, int) or floor_id < 1:
        return create_structured_error("InvalidInput", f"floor_id must be an integer >= 1, got {floor_id}", debug=debug)
    if not isinstance(outcome, str) or not outcome:
        return create_structured_error("InvalidInput", "outcome must be a non-empty string.", debug=debug)

    # Default values as per requirements
    dominant_damage_type = "unknown"
    most_used_skill = "unknown"
    clear_time_seconds = 0.0
    exploration_percent = 0.0
    notes = []

    # Outcome-specific adjustments
    if outcome == "VICTORY_ASCEND":
        death_event = False
        mutation_triggered = False
        notes.append("Victory Ascend residue.")
    elif outcome == "DEFEAT_DROP":
        death_event = True
        mutation_triggered = True # Defeat drops *trigger* mutations
        notes.append("Defeat Drop residue.")
    elif outcome == "RETREAT_TO_HUB":
        death_event = False
        mutation_triggered = False
        notes.append("Retreat to Hub residue.")
    elif outcome == "EXIT_GAME":
        death_event = False
        mutation_triggered = False
        notes.append("Exit Game residue.")
    else:
        _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "WARNING", "UnknownOutcome", f"make_residue_record called with unknown outcome: {outcome}", {"outcome": outcome}, debug)
        notes.append(f"Residue from unknown outcome: {outcome}.")

    residue_record = {
        "residue_id": str(uuid.uuid4()),
        "floor_id": floor_id,
        "outcome": outcome,
        "dominant_damage_type": dominant_damage_type,
        "most_used_skill": most_used_skill,
        "clear_time_seconds": clear_time_seconds,
        "exploration_percent": exploration_percent,
        "party_size": party_size,
        "death_event": death_event,
        "mutation_triggered": mutation_triggered,
        "notes": notes
    }
    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "ResidueRecordCreated", f"Residue record created for floor {floor_id} with outcome {outcome}.", {"record": residue_record}, debug)
    return create_structured_success(residue_record, debug=debug)


def get_or_create_floor_memory(tower_state, floor_id, layout_seed='unknown_seed', debug=False):
    """
    Gets the floor memory record for a floor_id from tower_state, or creates a new one if missing.
    """
    if not isinstance(tower_state, dict) or "floor_memory" not in tower_state:
        return create_structured_error("InvalidTowerState", "Tower state is invalid or missing 'floor_memory'.", debug=debug)
    if not isinstance(floor_id, int) or floor_id < 1:
        return create_structured_error("InvalidInput", f"floor_id must be an integer >= 1, got {floor_id}", debug=debug)

    for fm in tower_state["floor_memory"]:
        if fm.get("floor_id") == floor_id:
            _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "FloorMemoryFound", f"Existing floor memory found for floor {floor_id}.", {"floor_id": floor_id}, debug)
            return create_structured_success(fm, debug=debug)
    
    # If not found, create a new minimal floor memory record
    new_floor_memory = {
        "floor_id": floor_id,
        "visit_count": 0, # Will be incremented by write_residue_to_tower_state
        "death_count": 0,
        "victory_count": 0,
        "stability": 1.0,
        "deviation": 0.0,
        "mutation_level": 0,
        "known_layout_seed": layout_seed,
        "active_mutations": [],
        "discovered_easter_eggs": [],
        "unclaimed_easter_eggs": [],
        "residue_history": []
    }
    tower_state["floor_memory"].append(new_floor_memory)
    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "FloorMemoryCreated", f"New floor memory created for floor {floor_id}.", {"floor_id": floor_id}, debug)
    return create_structured_success(new_floor_memory, debug=debug)


def write_residue_to_tower_state(tower_state, residue_record, debug=False):
    """
    Appends a residue record to the appropriate floor_memory entry in tower_state
    and updates floor memory stats.
    """
    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "WriteResidueToTowerState", f"Writing residue record {residue_record.get('residue_id')} to floor {residue_record.get('floor_id')}.", {"record": residue_record}, debug)

    if not isinstance(tower_state, dict) or "floor_memory" not in tower_state:
        return create_structured_error("InvalidTowerState", "Tower state is invalid or missing 'floor_memory'.", debug=debug)
    if not isinstance(residue_record, dict) or "floor_id" not in residue_record or "outcome" not in residue_record:
        return create_structured_error("InvalidInput", "Residue record is invalid or missing 'floor_id' or 'outcome'.", debug=debug)

    floor_id = residue_record["floor_id"]
    outcome = residue_record["outcome"]

    # Get or create floor memory
    floor_memory_result = get_or_create_floor_memory(tower_state, floor_id, debug=debug)
    if not floor_memory_result["ok"]:
        return create_structured_error("FloorMemoryError", f"Failed to get or create floor memory for floor {floor_id}: {floor_memory_result['message']}", debug=debug)
    
    floor_memory = floor_memory_result["payload"]

    # Increment visit count (only if first time this session, simplified for MVP)
    # For MVP, we'll increment every time a record is written for that floor_id
    floor_memory["visit_count"] = floor_memory.get("visit_count", 0) + 1

    # Update counts based on outcome
    if outcome == "VICTORY_ASCEND":
        floor_memory["victory_count"] = floor_memory.get("victory_count", 0) + 1
    elif outcome == "DEFEAT_DROP":
        floor_memory["death_count"] = floor_memory.get("death_count", 0) + 1
        # For MVP, a DEFEAT_DROP also implies a mutation level increase and active mutation
        floor_memory["mutation_level"] = floor_memory.get("mutation_level", 0) + 1
        if "mvp_defeat_mutation" not in floor_memory["active_mutations"]:
            floor_memory["active_mutations"].append("mvp_defeat_mutation")
        _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "DefeatMutationApplied", f"Applied MVP defeat mutation to floor {floor_id}. New mutation_level: {floor_memory['mutation_level']}", {"floor_id": floor_id, "mutation_level": floor_memory["mutation_level"]}, debug)
    
    # Append residue to history
    floor_memory.get("residue_history", []).append(residue_record)

    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "FloorMemoryUpdated", f"Floor memory for floor {floor_id} updated.", {"floor_memory": floor_memory}, debug)
    return create_structured_success(tower_state, debug=debug)


def write_mvp_outcome_residue(tower_state, floor_id, outcome, debug=False):
    """
    Creates a residue record for an MVP floor outcome and writes it to tower_state.
    """
    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "WriteMVPOccurrenceResidue", f"Writing MVP outcome residue for floor {floor_id}, outcome {outcome}.", {"floor_id": floor_id, "outcome": outcome}, debug)

    # 1. Make residue record
    residue_record_result = make_residue_record(floor_id, outcome, debug=debug)
    if not residue_record_result["ok"]:
        return create_structured_error("ResidueRecordError", f"Failed to create residue record: {residue_record_result['message']}", debug=debug)
    
    residue_record = residue_record_result["payload"]

    # 2. Validate residue record against its schema
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)

    validation_result = json_save_manager.validate_json(residue_record, _RESIDUE_RECORD_SCHEMA_PATH, debug=debug)
    if not validation_result["ok"]:
        return create_structured_error("ResidueSchemaValidationFailure", f"Created residue record failed schema validation: {validation_result['message']}", debug=debug)

    # 3. Write residue to tower state
    write_result = write_residue_to_tower_state(tower_state, residue_record, debug=debug)
    if not write_result["ok"]:
        return create_structured_error("WriteResidueError", f"Failed to write residue to tower state: {write_result['message']}", debug=debug)

    _log_debug_event("TOWER-ENGINE-025", "mvp_residue_writer", "INFO", "MVPOccurrenceResidueWritten", f"MVP outcome residue written successfully for floor {floor_id}, outcome {outcome}.", debug_enabled=debug)
    return create_structured_success({
        "tower_state": tower_state,
        "residue_record": residue_record,
        "floor_memory": next((fm for fm in tower_state["floor_memory"] if fm["floor_id"] == floor_id), None)
    }, debug=debug)
