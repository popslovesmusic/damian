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

# Import relevant bootstrappers and drivers
try:
    from engine.core.runtime import state_machine_driver
    _state_machine_driver_available = True
except ImportError:
    _state_machine_driver_available = False

try:
    from engine.save.bootstrap import tower_state_bootstrapper
    _tower_state_bootstrapper_available = True
except ImportError:
    _tower_state_bootstrapper_available = False

try:
    from engine.player.bootstrap import player_progression_bootstrapper
    _player_progression_bootstrapper_available = True
except ImportError:
    _player_progression_bootstrapper_available = False

try:
    from engine.domain.bootstrap import domain_state_bootstrapper
    _domain_state_bootstrapper_available = True
except ImportError:
    _domain_state_bootstrapper_available = False


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
        _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_default_runtime_paths(base_save_dir='saves/local_mvp'):
    """
    Generates default paths for saving/loading MVP runtime components.
    """
    return {
        "state_machine_states": "engine/core/state_machine/game_loop_states.json",
        "state_machine_transitions": "engine/core/state_machine/game_loop_transitions.json",
        "tower_state": os.path.join(base_save_dir, "tower_state.json"),
        "tower_state_schema": "engine/save/schemas/tower_state.schema.json",
        "player_progression": os.path.join(base_save_dir, "player_progression.json"),
        "player_progression_schema": "engine/player/contracts/player_progression_state.schema.json",
        "domain_state": os.path.join(base_save_dir, "domain_state.json"),
        "domain_state_schema": "engine/domain/contracts/domain_state.schema.json",
    }


def startup_mvp_runtime(paths=None, create_if_missing=True, debug=False):
    """
    Orchestrates the startup of the MVP runtime.
    """
    context = {
        "ok": True,
        "engine_version": "0.0.1",
        "content_pack_id": "damian",
        "state_machine": None,
        "state_context": None,
        "tower_state": None,
        "player_progression": None,
        "domain_state": None,
        "errors": [],
        "debug_enabled": debug
    }

    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "StartupStart", "Starting MVP runtime orchestration.", context={"create_if_missing": create_if_missing}, debug_enabled=debug)

    if not paths:
        paths = make_default_runtime_paths()
        _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "DEBUG", "DefaultPathsUsed", "Using default runtime paths.", context=paths, debug_enabled=debug)

    # 1. Load State Machine
    if not _state_machine_driver_available:
        err = create_structured_error("DependencyError", "state_machine_driver is not available for orchestrator.", debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context

    sm_load_result = state_machine_driver.load_state_machine(paths["state_machine_states"], paths["state_machine_transitions"], debug=debug)
    if not sm_load_result["ok"]:
        err = create_structured_error("StateMachineLoadFailure", sm_load_result["message"], path=sm_load_result.get("path", ""), debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context
    context["state_machine"] = sm_load_result["payload"]
    context["state_context"] = state_machine_driver.create_runtime_context("BOOT_ENGINE")
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "StateMachineLoaded", "Game Loop State Machine loaded.", debug_enabled=debug)

    # 2. Bootstrap Tower State
    if not _tower_state_bootstrapper_available:
        err = create_structured_error("DependencyError", "tower_state_bootstrapper is not available for orchestrator.", debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context

    tower_bootstrap_result = tower_state_bootstrapper.bootstrap_tower_state(
        paths["tower_state"], paths["tower_state_schema"], create_if_missing=create_if_missing, debug=debug
    )
    if not tower_bootstrap_result["ok"]:
        err = create_structured_error("TowerStateBootstrapFailure", tower_bootstrap_result["message"], path=tower_bootstrap_result.get("path", ""), debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context
    context["tower_state"] = tower_bootstrap_result["payload"]
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "TowerStateBootstrapped", "Tower State initialized.", debug_enabled=debug)

    # 3. Bootstrap Player Progression
    if not _player_progression_bootstrapper_available:
        err = create_structured_error("DependencyError", "player_progression_bootstrapper is not available for orchestrator.", debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context

    player_bootstrap_result = player_progression_bootstrapper.bootstrap_player_progression(
        paths["player_progression"], paths["player_progression_schema"], create_if_missing=create_if_missing, debug=debug
    )
    if not player_bootstrap_result["ok"]:
        err = create_structured_error("PlayerProgressionBootstrapFailure", player_bootstrap_result["message"], path=player_bootstrap_result.get("path", ""), debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context
    context["player_progression"] = player_bootstrap_result["payload"]
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "PlayerProgressionBootstrapped", "Player Progression initialized.", debug_enabled=debug)


    # 4. Bootstrap Domain State
    if not _domain_state_bootstrapper_available:
        err = create_structured_error("DependencyError", "domain_state_bootstrapper is not available for orchestrator.", debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context

    domain_bootstrap_result = domain_state_bootstrapper.bootstrap_domain_state(
        paths["domain_state"], paths["domain_state_schema"], create_if_missing=create_if_missing, debug=debug
    )
    if not domain_bootstrap_result["ok"]:
        err = create_structured_error("DomainStateBootstrapFailure", domain_bootstrap_result["message"], path=domain_bootstrap_result.get("path", ""), debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        return context
    context["domain_state"] = domain_bootstrap_result["payload"]
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "DomainStateBootstrapped", "Domain State initialized.", debug_enabled=debug)


    # 5. Validate final startup context
    validation_result = validate_startup_context(context, debug=debug)
    if not validation_result["ok"]:
        err = create_structured_error("StartupContextValidationFailure", validation_result["message"], debug=debug)
        context["ok"] = False
        context["errors"].append(err)
        _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "CRITICAL", "StartupFailure", "MVP Runtime startup failed validation.", context=context["errors"], debug_enabled=debug)
        return context
    
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "StartupSuccess", "MVP Runtime started successfully.", debug_enabled=debug)
    return context

def validate_startup_context(context, debug=False):
    """
    Performs a final validation of the entire startup context.
    """
    if not context["state_machine"]:
        return create_structured_error("ValidationFailure", "State machine not loaded in context.", debug=debug)
    if not context["state_context"]:
        return create_structured_error("ValidationFailure", "State context not initialized.", debug=debug)
    if not context["tower_state"]:
        return create_structured_error("ValidationFailure", "Tower state not bootstrapped.", debug=debug)
    if not context["player_progression"]:
        return create_structured_error("ValidationFailure", "Player progression not bootstrapped.", debug=debug)
    if not context["domain_state"]:
        return create_structured_error("ValidationFailure", "Domain state not bootstrapped.", debug=debug)
    if not context["ok"] or context["errors"]:
        return create_structured_error("ValidationFailure", "Context contains errors from prior steps.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "ContextValidationSuccess", "Startup context is valid.", debug_enabled=debug)
    return create_structured_success(True, debug=debug)


def shutdown_mvp_runtime(context, debug=False):
    """
    Performs a graceful shutdown of the MVP runtime.
    In this minimal implementation, it primarily logs the shutdown.
    """
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "ShutdownStart", "Initiating MVP Runtime shutdown.", debug_enabled=debug)
    # In a real scenario, this would involve saving state, closing connections, etc.
    _log_debug_event("TOWER-ENGINE-022", "mvp_startup_orchestrator", "INFO", "ShutdownComplete", "MVP Runtime shutdown complete.", debug_enabled=debug)
    return create_structured_success(True, debug=debug)
