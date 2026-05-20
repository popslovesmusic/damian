import os
import json
import sys
import datetime
import uuid
import shutil
import tempfile
from engine.io.runtime import artifact_policy

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import mvp_outcome_pipeline
try:
    from engine.prototype.runtime import mvp_outcome_pipeline
    _mvp_outcome_pipeline_available = True
except ImportError:
    _mvp_outcome_pipeline_available = False

# Import bootstrappers
try:
    from engine.save.bootstrap import tower_state_bootstrapper
    from engine.player.bootstrap import player_progression_bootstrapper
    from engine.domain.bootstrap import domain_state_bootstrapper
    _bootstrappers_available = True
except ImportError:
    _bootstrappers_available = False

# Import json_save_manager
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
        _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_scripted_sequence(name='default_sequence'):
    """
    Creates a default scripted sequence for MVP testing.
    """
    if name == 'default_sequence':
        return [
            "VICTORY_ASCEND",
            "VICTORY_ASCEND",
            "DEFEAT_DROP",
            "VICTORY_ASCEND",
            "EXIT_GAME"
        ]
    return [] # Return empty for other names for now

def load_simulation_results(path, debug=False):
    """
    Loads a simulation result file.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "DEBUG", "LoadSimulationResults", f"Loading simulation results from {path}.", {"path": path}, debug)
    result = json_save_manager.load_json(path, debug=debug)
    
    if result["ok"]:
        _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "SimulationResultsLoaded", f"Successfully loaded simulation results from {path}.", {"path": path}, debug)
        return create_structured_success(result["payload"], path, debug=debug)
    else:
        _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "ERROR", "SimulationResultsLoadFailure", f"Failed to load simulation results from {path}: {result['message']}", {"path": path, "error": result}, debug)
        return result


def summarize_simulation_result(result, debug=False):
    """
    Creates a structured summary of a simulation result.
    """
    if not isinstance(result, dict) or "ok" not in result:
        return create_structured_error("InvalidInput", "Invalid simulation result format.", debug=debug)

    summary = {
        "ok": result.get("ok", False),
        "sequence_name": result.get("sequence_name", "N/A"),
        "steps_executed": result.get("steps_executed", 0),
        "final_floor": result.get("final_floor", 0),
        "highest_floor_reached": result.get("highest_floor_reached", 0),
        "mutation_events_triggered": result.get("mutation_events_triggered", 0),
        "residue_records_written": result.get("residue_records_written", 0),
        "final_tower_state_path": result.get("final_tower_state_path", "N/A"),
        "errors": result.get("errors", [])
    }
    _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "SimulationSummary", "Simulation summary generated.", {"summary": summary}, debug)
    return create_structured_success(summary, debug=debug)


def run_scripted_simulation(sequence, save_dir='saves/simulations', debug=False, write_to_disk=False):
    """
    Runs a deterministic scripted simulation through the MVP pipeline.
    """
    _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "SimulationStart", "Starting scripted simulation.", {"sequence_length": len(sequence)}, debug)

    if not _mvp_outcome_pipeline_available or not _bootstrappers_available or not _json_save_manager_available:
        return create_structured_error("DependencyError", "One or more core MVP modules are unavailable.", debug=debug)

    simulation_id = f"sim_{uuid.uuid4().hex[:8]}"
    allow_writes = bool(write_to_disk) and artifact_policy.allow_artifact_writes(default=True)
    if allow_writes:
        simulation_output_dir = os.path.join(save_dir, simulation_id)
        os.makedirs(simulation_output_dir, exist_ok=True)
    else:
        # Containment mode: avoid writing artifacts into the repo by default.
        # Simulation still requires filesystem paths for bootstrapping, so we use a temp dir.
        simulation_output_dir = tempfile.mkdtemp(prefix="tower_sim_")
    
    # Paths for this simulation run
    sim_paths = {
        "tower_state": os.path.join(simulation_output_dir, "tower_state.json"),
        "player_progression": os.path.join(simulation_output_dir, "player_progression.json"),
        "domain_state": os.path.join(simulation_output_dir, "domain_state.json"),
        "tower_state_schema": "engine/save/schemas/tower_state.schema.json",
        "player_progression_schema": "engine/player/contracts/player_progression_state.schema.json",
        "domain_state_schema": "engine/domain/contracts/domain_state.schema.json",
    }
    # Pass along state machine paths from base definition
    sim_paths["state_machine_states"] = "engine/core/state_machine/game_loop_states.json"
    sim_paths["state_machine_transitions"] = "engine/core/state_machine/game_loop_transitions.json"


    # 1. Bootstrap MVP Runtime
    # We need a context similar to what mvp_startup_orchestrator would provide,
    # but only for the necessary save files and state machine definitions for this sim.
    # For MVP, we bootstrap directly to get the current state for this simulation.
    _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "DEBUG", "BootstrappingSimulationContext", "Bootstrapping initial state for simulation.", debug_enabled=debug)

    # Note: Reusing bootstrapping logic from Orchestrator-like fashion, for simplicity here.
    # In a full engine, mvp_startup_orchestrator would provide the initial context.
    initial_tower_state_result = tower_state_bootstrapper.bootstrap_tower_state(sim_paths["tower_state"], sim_paths["tower_state_schema"], create_if_missing=True, debug=debug)
    if not initial_tower_state_result["ok"]:
        return create_structured_error("SimulationInitFailure", f"Failed to bootstrap tower state: {initial_tower_state_result['message']}", debug=debug)
    current_tower_state = initial_tower_state_result["payload"]

    initial_player_progression_result = player_progression_bootstrapper.bootstrap_player_progression(sim_paths["player_progression"], sim_paths["player_progression_schema"], create_if_missing=True, debug=debug)
    if not initial_player_progression_result["ok"]:
        return create_structured_error("SimulationInitFailure", f"Failed to bootstrap player progression: {initial_player_progression_result['message']}", debug=debug)
    # current_player_progression = initial_player_progression_result["payload"] # Not directly used by pipeline currently

    initial_domain_state_result = domain_state_bootstrapper.bootstrap_domain_state(sim_paths["domain_state"], sim_paths["domain_state_schema"], create_if_missing=True, debug=debug)
    if not initial_domain_state_result["ok"]:
        return create_structured_error("SimulationInitFailure", f"Failed to bootstrap domain state: {initial_domain_state_result['message']}", debug=debug)
    # current_domain_state = initial_domain_state_result["payload"] # Not directly used by pipeline currently


    steps_executed = 0
    mutation_events_triggered = 0
    residue_records_written = 0
    errors = []

    for step_outcome in sequence:
        _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "SimulationStep", f"Executing step {steps_executed + 1}: {step_outcome}", {"current_floor": current_tower_state.get("current_floor")}, debug)
        
        pipeline_result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(current_tower_state, step_outcome, debug=debug)
        
        if not pipeline_result["ok"]:
            errors.append(pipeline_result["error"])
            _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "ERROR", "PipelineFailure", f"Pipeline failed at step {steps_executed + 1} with outcome {step_outcome}: {pipeline_result['error']['message']}", debug_enabled=debug)
            # Continue simulation or break? For MVP, we'll break on first error.
            break

        current_tower_state = pipeline_result["tower_state"] # Update tower state from pipeline result
        steps_executed += 1

        if pipeline_result["residue_result"] and pipeline_result["residue_result"]["ok"]:
            residue_records_written += 1
            _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "DEBUG", "ResidueWritten", "Residue record written.", {"record": pipeline_result["residue_result"]["payload"]["residue_record"]}, debug_enabled=debug)
        
        if pipeline_result["mutation_applied"]:
            mutation_events_triggered += 1
            _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "DEBUG", "MutationApplied", "Mutation stub applied.", {"event": pipeline_result["mutation_result"]["payload"]["mutation_event"]}, debug_enabled=debug)

        if pipeline_result["shutdown_requested"]:
            _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "ShutdownRequested", "Shutdown requested by pipeline.", debug_enabled=debug)
            break
    
    # Save final tower state
    final_tower_state_path = os.path.join(simulation_output_dir, "final_tower_state.json")
    if allow_writes:
        save_result = tower_state_bootstrapper.save_tower_state(final_tower_state_path, current_tower_state, sim_paths["tower_state_schema"], debug=debug)
        if not save_result["ok"]:
            errors.append(create_structured_error("FinalSaveFailure", f"Failed to save final tower state: {save_result['message']}", path=final_tower_state_path, debug=debug))

    # Compile simulation result
    sim_result = {
        "ok": not bool(errors),
        "sequence_name": sequence_name_from_sequence(sequence),
        "steps_executed": steps_executed,
        "final_floor": current_tower_state.get("current_floor", 0),
        "highest_floor_reached": current_tower_state.get("highest_floor_reached", 0),
        "mutation_events_triggered": mutation_events_triggered,
        "residue_records_written": residue_records_written,
        "final_tower_state_path": final_tower_state_path,
        "errors": errors
    }
    
    # Save overall simulation result artifact
    sim_artifact_path = os.path.join(simulation_output_dir, f"{simulation_id}_result.json")
    if allow_writes:
        json_save_manager.save_json(sim_artifact_path, sim_result, debug=debug) # Save without validation for flexibility
    
    _log_debug_event("TOWER-ENGINE-028", "mvp_scripted_simulation", "INFO", "SimulationComplete", "Scripted simulation finished.", {"result": sim_result, "writes_enabled": allow_writes}, debug_enabled=debug)

    # If using containment temp dir, clean up to prevent lingering artifacts.
    if not allow_writes:
        try:
            shutil.rmtree(simulation_output_dir, ignore_errors=True)
        except Exception:
            pass

    return create_structured_success(sim_result, path=(sim_artifact_path if allow_writes else ""), debug=debug)

def sequence_name_from_sequence(sequence):
    """Generates a simple name from a sequence."""
    return "_".join(s.replace("_", "").lower() for s in sequence) + "_sequence"
