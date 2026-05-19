import os
import json
import datetime
import sys

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

    # Import mvp_floor_mutation_stub
try:
    from engine.mutation.runtime import mvp_floor_mutation_stub
    _mvp_floor_mutation_stub_available = True
except ImportError:
    _mvp_floor_mutation_stub_available = False

# Import mvp_survivor_mark_system
try:
    from engine.easter_eggs.runtime import mvp_survivor_mark_system
    _mvp_survivor_mark_system_available = True
except ImportError:
    _mvp_survivor_mark_system_available = False

# Import mvp_floor_progression
try:
    from engine.progression.runtime import mvp_floor_progression
    _mvp_floor_progression_available = True
except ImportError:
    _mvp_floor_progression_available = False

# Import mvp_residue_writer
try:
    from engine.residue.runtime import mvp_residue_writer
    _mvp_residue_writer_available = True
except ImportError:
    _mvp_residue_writer_available = False


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
        _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def validate_pipeline_result(result, debug=False):
    """
    Validates the structure and basic integrity of a pipeline result.
    """
    required_keys = ["ok", "outcome", "previous_floor", "current_floor", "tower_state", 
                     "progression_result", "residue_result", "mutation_result", "mutation_applied",
                     "survivor_mark_result", "survivor_mark_attached", "error"]
    
    for key in required_keys:
        if key not in result:
            return create_structured_error("InvalidResultStructure", f"Missing key '{key}' in pipeline result.", debug=debug)
    
    if result["ok"] and result["error"] is not None:
        return create_structured_error("InvalidResult", "Result is ok but contains an error object.", debug=debug)
    if not result["ok"] and result["error"] is None:
        return create_structured_error("InvalidResult", "Result is not ok but has no error object.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "PipelineResultValidated", "Pipeline result structure is valid.", debug_enabled=debug)
    return create_structured_success(True, debug=debug)


def resolve_victory_pipeline(tower_state, debug=False):
    """
    Handles the pipeline for VICTORY_ASCEND outcome.
    """
    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "VictoryPipeline", "Starting victory pipeline.", debug_enabled=debug)

    if not _mvp_floor_progression_available:
        return create_structured_error("DependencyError", "mvp_floor_progression is not available.", debug=debug)
    if not _mvp_residue_writer_available:
        return create_structured_error("DependencyError", "mvp_residue_writer is not available.", debug=debug)

    previous_floor = tower_state.get("current_floor")

    # 1. Apply progression ascend
    progression_result = mvp_floor_progression.apply_victory_ascend(tower_state, debug=debug)
    if not progression_result["ok"]:
        return create_structured_error("ProgressionFailure", progression_result["error"]["message"], debug=debug)
    
    updated_tower_state = progression_result["tower_state"]
    current_floor = updated_tower_state["current_floor"]

    # 2. Write VICTORY_ASCEND residue to previous_floor
    # Residue is written for the floor just completed.
    residue_result = mvp_residue_writer.write_mvp_outcome_residue(updated_tower_state, previous_floor, "VICTORY_ASCEND", debug=debug)
    if not residue_result["ok"]:
        return create_structured_error("ResidueWriteFailure", residue_result["error"]["message"], debug=debug)

    # 3. No mutation stub for victory, and no survivor mark
    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "NoMutation", "No mutation applied for VICTORY_ASCEND.", debug_enabled=debug)

    return {
        "ok": True,
        "outcome": "VICTORY_ASCEND",
        "previous_floor": previous_floor,
        "current_floor": current_floor,
        "tower_state": updated_tower_state,
        "progression_result": progression_result,
        "residue_result": residue_result,
        "mutation_result": None,
        "mutation_applied": False,
        "survivor_mark_result": None,
        "survivor_mark_attached": False,
        "error": None
    }


def resolve_defeat_drop_pipeline(tower_state, debug=False):
    """
    Handles the pipeline for DEFEAT_DROP outcome.
    """
    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "DefeatPipeline", "Starting defeat drop pipeline.", debug_enabled=debug)

    if not _mvp_floor_progression_available:
        return create_structured_error("DependencyError", "mvp_floor_progression is not available.", debug=debug)
    if not _mvp_residue_writer_available:
        return create_structured_error("DependencyError", "mvp_residue_writer is not available.", debug=debug)
    if not _mvp_floor_mutation_stub_available:
        return create_structured_error("DependencyError", "mvp_floor_mutation_stub is not available.", debug=debug)
    if not _mvp_survivor_mark_system_available:
        return create_structured_error("DependencyError", "mvp_survivor_mark_system is not available.", debug=debug)


    previous_floor = tower_state.get("current_floor")

    # 1. Apply progression defeat drop
    progression_result = mvp_floor_progression.apply_defeat_drop(tower_state, debug=debug)
    if not progression_result["ok"]:
        return create_structured_error("ProgressionFailure", progression_result["error"]["message"], debug=debug)
    
    updated_tower_state = progression_result["tower_state"]
    current_floor = updated_tower_state["current_floor"]

    # 2. Write DEFEAT_DROP residue to returned current_floor (which is the new floor)
    residue_result = mvp_residue_writer.write_mvp_outcome_residue(updated_tower_state, current_floor, "DEFEAT_DROP", debug=debug)
    if not residue_result["ok"]:
        return create_structured_error("ResidueWriteFailure", residue_result["error"]["message"], debug=debug)
    
    triggering_residue_id = residue_result["payload"]["residue_record"]["residue_id"] if residue_result["ok"] and "payload" in residue_result and "residue_record" in residue_result["payload"] else "unknown_residue"


    # 3. Apply replay floor mutation stub to returned current_floor
    mutation_result = mvp_floor_mutation_stub.apply_replay_floor_mutation_stub(updated_tower_state, current_floor, triggering_residue_id, debug=debug)
    if not mutation_result["ok"]:
        return create_structured_error("MutationApplicationFailure", mutation_result["error"]["message"], debug=debug)

    # 4. Create and attach survivor mark
    # For MVP, we'll attach one mark per defeat-drop
    mark_result = mvp_survivor_mark_system.make_survivor_mark(current_floor, triggering_residue_id, mark_index=1, debug=debug)
    if not mark_result["ok"]:
        return create_structured_error("SurvivorMarkCreationFailure", mark_result["error"]["message"], debug=debug)
    
    survivor_mark = mark_result["payload"]
    # Get the floor memory for the current floor
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(updated_tower_state, current_floor, debug=debug)
    if not floor_memory_result["ok"]:
        return create_structured_error("FloorMemoryError", f"Failed to get floor memory for mark attachment: {floor_memory_result['message']}", debug=debug)
    
    floor_memory = floor_memory_result["payload"]
    attach_mark_result = mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, survivor_mark, debug=debug)
    if not attach_mark_result["ok"]:
        return create_structured_error("SurvivorMarkAttachmentFailure", attach_mark_result["error"]["message"], debug=debug)

    return {
        "ok": True,
        "outcome": "DEFEAT_DROP",
        "previous_floor": previous_floor,
        "current_floor": current_floor,
        "tower_state": updated_tower_state,
        "progression_result": progression_result,
        "residue_result": residue_result,
        "mutation_result": mutation_result,
        "mutation_applied": True,
        "survivor_mark_result": survivor_mark, # Return the created mark
        "survivor_mark_attached": True,
        "error": None
    }


def resolve_mvp_floor_outcome(tower_state, outcome, debug=False):
    """
    Resolves a floor outcome through the MVP pipeline (progression, residue, mutation, survivor marks).
    """
    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "PipelineStart", f"Starting MVP pipeline for outcome: {outcome}", {"outcome": outcome, "tower_state_before": tower_state}, debug)

    if not isinstance(tower_state, dict):
        return create_structured_error("InvalidTowerState", "Provided tower_state is not a dictionary.", debug=debug)
    
    result = {}
    if outcome == "VICTORY_ASCEND":
        result = resolve_victory_pipeline(tower_state, debug=debug)
    elif outcome == "DEFEAT_DROP":
        result = resolve_defeat_drop_pipeline(tower_state, debug=debug)
    elif outcome == "RETREAT_TO_HUB":
        # For MVP, retreat simply applies progression and writes residue, no mutation or mark.
        if not _mvp_floor_progression_available:
            return create_structured_error("DependencyError", "mvp_floor_progression is not available.", debug=debug)
        if not _mvp_residue_writer_available:
            return create_structured_error("DependencyError", "mvp_residue_writer is not available.", debug=debug)
        
        previous_floor = tower_state.get("current_floor")
        progression_result = mvp_floor_progression.resolve_floor_outcome(tower_state, outcome, debug=debug)
        if not progression_result["ok"]:
            return create_structured_error("ProgressionFailure", progression_result["error"]["message"], debug=debug)
        
        updated_tower_state = progression_result["tower_state"]
        current_floor = updated_tower_state["current_floor"]

        residue_result = mvp_residue_writer.write_mvp_outcome_residue(updated_tower_state, current_floor, outcome, debug=debug)
        if not residue_result["ok"]:
            return create_structured_error("ResidueWriteFailure", residue_result["error"]["message"], debug=debug)
        
        result = {
            "ok": True,
            "outcome": outcome,
            "previous_floor": previous_floor,
            "current_floor": current_floor,
            "tower_state": updated_tower_state,
            "progression_result": progression_result,
            "residue_result": residue_result,
            "mutation_result": None,
            "mutation_applied": False,
            "survivor_mark_result": None,
            "survivor_mark_attached": False,
            "error": None
        }
        _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "RetreatPipeline", "Retreat pipeline resolved.", debug_enabled=debug)
    elif outcome == "EXIT_GAME":
        # For MVP, exit simply applies progression and writes residue, no mutation or mark.
        if not _mvp_floor_progression_available:
            return create_structured_error("DependencyError", "mvp_floor_progression is not available.", debug=debug)
        if not _mvp_residue_writer_available:
            return create_structured_error("DependencyError", "mvp_residue_writer is not available.", debug=debug)

        previous_floor = tower_state.get("current_floor")
        progression_result = mvp_floor_progression.resolve_floor_outcome(tower_state, outcome, debug=debug)
        if not progression_result["ok"]:
            return create_structured_error("ProgressionFailure", progression_result["error"]["message"], debug=debug)

        updated_tower_state = progression_result["tower_state"]
        current_floor = updated_tower_state["current_floor"]

        residue_result = mvp_residue_writer.write_mvp_outcome_residue(updated_tower_state, current_floor, outcome, debug=debug)
        if not residue_result["ok"]:
            return create_structured_error("ResidueWriteFailure", residue_result["error"]["message"], debug=debug)

        result = {
            "ok": True,
            "outcome": outcome,
            "previous_floor": previous_floor,
            "current_floor": current_floor,
            "tower_state": updated_tower_state,
            "progression_result": progression_result,
            "residue_result": residue_result,
            "mutation_result": None,
            "mutation_applied": False,
            "survivor_mark_result": None,
            "survivor_mark_attached": False,
            "error": None
        }
        _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "ExitGamePipeline", "Exit game pipeline resolved.", debug_enabled=debug)
    else:
        result = create_structured_error("InvalidOutcome", f"Unsupported outcome: {outcome}", debug=debug)

    # Validate final result structure
    validation_final_result = validate_pipeline_result(result, debug=debug)
    if not validation_final_result["ok"]:
        final_error = create_structured_error("PipelineResultInvalid", validation_final_result["message"], debug=debug)
        result["ok"] = False
        result["error"] = final_error
        _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "CRITICAL", "PipelineResultCorrupted", "Final pipeline result structure is invalid.", context={"result": result}, debug_enabled=debug)

    _log_debug_event("TOWER-ENGINE-027", "mvp_outcome_pipeline", "INFO", "PipelineComplete", f"MVP pipeline for outcome {outcome} completed.", {"result": result}, debug)
    return result