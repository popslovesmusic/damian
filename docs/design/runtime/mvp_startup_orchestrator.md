# Tower Engine Minimal Playable Prototype (MVP) Startup Orchestrator

This document defines the implementation and behavior of the `mvp_startup_orchestrator`, the central component responsible for initializing the Tower Engine's minimal playable runtime. It orchestrates the loading of core game loop definitions and the bootstrapping of essential game states (Tower State, Player Progression, Domain State) by leveraging previously implemented modules, ensuring a consistent and failure-safe startup sequence.

## Core Principles

*   **Runtime Implementation:** This patch involves writing functional code to manage the overall game startup.
*   **Orchestration, Not Implementation:** The orchestrator's role is to coordinate existing bootstrappers and drivers. It explicitly avoids re-implementing logic handled by other modules.
*   **Debug Hooks Integrated:** Startup and shutdown processes are instrumented with optional debug logging, providing traceable insights into the initialization sequence.
*   **Failure-Safe Startup:** The orchestrator is designed to gracefully handle failures from any component bootstrap or load operation, collecting errors and returning an overall failed context without crashing.
*   **Configurable Paths:** Default paths for save files and schemas can be overridden, allowing for flexible testing and future deployment configurations.
*   **No Gameplay Loop Execution:** The orchestrator prepares the runtime context but does not execute the game loop itself. That responsibility lies with the `state_machine_driver` in conjunction with higher-level game logic.

## MVP Startup Orchestrator (`engine/core/orchestrator/mvp_startup_orchestrator.py`)

This Python module provides the functions for orchestrating the MVP runtime startup and shutdown.

### Required Functions:

*   `make_default_runtime_paths(base_save_dir='saves/local_mvp')`:
    *   **Objective:** Generates a dictionary of default file paths for the state machine definitions and the various game state save files.
    *   **Output:** Returns a dictionary of paths.
*   `startup_mvp_runtime(paths=None, create_if_missing=True, debug=False)`:
    *   **Objective:** The primary entry point for initializing the MVP runtime.
    *   **Sequence:**
        1.  Loads the game loop state machine using `state_machine_driver.load_state_machine`.
        2.  Creates an initial state context using `state_machine_driver.create_runtime_context`.
        3.  Bootstraps the Tower State using `tower_state_bootstrapper.bootstrap_tower_state`.
        4.  Bootstraps the Player Progression State using `player_progression_bootstrapper.bootstrap_player_progression`.
        5.  Bootstraps the Domain State using `domain_state_bootstrapper.bootstrap_domain_state`.
        6.  Performs a final validation of the assembled `startup_context`.
    *   **Behavior:** Collects any structured errors encountered during bootstrap steps. If `create_if_missing` is true, missing save files will trigger default creation.
    *   **Output:** Returns a `runtime_context_shape` dictionary, with `ok=True` for success, or `ok=False` and `errors` populated for failure.
*   `validate_startup_context(context, debug=False)`:
    *   **Objective:** Performs a final check on the assembled runtime context to ensure all critical components are present and valid.
    *   **Output:** Returns `{"ok": True, "payload": True}` or a structured error.
*   `shutdown_mvp_runtime(context, debug=False)`:
    *   **Objective:** Performs a graceful shutdown of the MVP runtime.
    *   **Behavior:** For this minimal implementation, it primarily logs the shutdown event. In future iterations, it would handle saving final states, releasing resources, etc.
    *   **Output:** Returns `{"ok": True, "payload": True}` or a structured error.

## Runtime Context Shape (`runtime_context_shape`)

This structured dictionary (`runtime_context_shape`) is returned by `startup_mvp_runtime` and contains all the initialized components and any errors encountered.

### Key Fields:

*   `ok`: Overall success status.
*   `engine_version`, `content_pack_id`: Core identifiers.
*   `state_machine`: The loaded game loop state machine.
*   `state_context`: The initial state machine runtime context.
*   `tower_state`, `player_progression`, `domain_state`: The bootstrapped game states.
*   `errors`: An array of structured error messages collected during startup.
*   `debug_enabled`: Reflects whether debugging was active during startup.

## Unit Tests (`engine/core/orchestrator/tests/test_mvp_startup_orchestrator.py`)

A comprehensive `pytest` suite verifies:
*   `make_default_runtime_paths` generates correct paths.
*   `startup_mvp_runtime` performs a clean startup when `create_if_missing=True`, creating all necessary save files.
*   `startup_mvp_runtime` correctly loads existing valid saves.
*   `startup_mvp_runtime` fails safely and collects errors when `create_if_missing=False` and saves are missing.
*   `startup_mvp_runtime` fails safely and collects errors when a component (e.g., Tower State) is invalid.
*   `shutdown_mvp_runtime` executes successfully.
*   Debug logging integration: `_log_debug_event` is called when `debug=True`, and the orchestrator remains functional if `debug_logger` is unavailable.

## MVP Startup Orchestrator Documentation (`docs/design/runtime/mvp_startup_orchestrator.md`)

This document details the responsibilities of the `mvp_startup_orchestrator`, its interaction with other bootstrappers/drivers, and its strict adherence to safe and structured startup management while enforcing the minimal viable product scope.
