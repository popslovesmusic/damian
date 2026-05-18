# Tower Engine Minimal Runtime State Machine Driver

This document outlines the design and implementation of the initial runtime driver for the Tower Engine's game loop state machine. This driver is responsible for loading the state machine definitions (states and transitions) from JSON files and safely stepping through valid transitions, providing structured debug output where configured. This is a foundational runtime component that will orchestrate the high-level game flow without implementing any specific gameplay logic.

## Core Principles

*   **Runtime Implementation Allowed:** This patch focuses on implementing the logic defined in prior architectural contracts.
*   **Debug Hooks Integrated:** The driver fully integrates with the debug logging system (TOWER-ENGINE-017A) to provide optional, structured diagnostics.
*   **No Gameplay Logic:** The driver's sole responsibility is state management and transition enforcement. It explicitly avoids any implementation of combat, floor generation, rendering, or multiplayer logic.
*   **Strict State Machine Enforcement:** All transitions must adhere to the defined `game_loop_transitions.json`. Invalid transitions are detected and result in structured errors.
*   **Failure-Safe Behavior:** The driver returns structured error messages for invalid operations (e.g., missing state machine definitions, invalid transitions) without crashing.
*   **External Data Loading:** State machine definitions are loaded from external JSON files using the `json_save_manager` (TOWER-ENGINE-017), ensuring data-driven configuration.

## State Machine Driver (`engine/core/runtime/state_machine_driver.py`)

This Python module provides the core functions for operating the game loop state machine.

### Required Functions:

*   `load_state_machine(states_path, transitions_path, debug=False)`:
    *   **Objective:** Loads the state definitions (`game_loop_states.json`) and transition rules (`game_loop_transitions.json`).
    *   **Behavior:** Uses `json_save_manager` to load files. Logs debug events for success/failure.
    *   **Output:** Returns `{"ok": True, "payload": machine}` (where `machine` is a dictionary with `states` and `transitions`) or a structured error.
*   `create_runtime_context(initial_state='BOOT_ENGINE')`:
    *   **Objective:** Initializes a runtime context object for tracking the current state, visited states, and any errors.
    *   **Output:** Returns `{"ok": True, "current_state": "...", "visited_states": [...], "last_error": None}`.
*   `can_transition(machine, from_state, to_state)`:
    *   **Objective:** Checks if a direct transition from `from_state` to `to_state` is allowed by the loaded `transitions` rules.
    *   **Output:** Returns `True` or `False`.
*   `step_transition(machine, context, to_state, debug=False)`:
    *   **Objective:** Attempts to move the state machine from `context['current_state']` to `to_state`.
    *   **Behavior:** Validates the transition using `can_transition`. If valid, updates `context['current_state']` and `context['visited_states']`. Logs debug events for valid and invalid transitions.
    *   **Output:** Returns `{"ok": True, "payload": updated_context}` or a structured error.
*   `run_scripted_path(machine, context, path, debug=False)`:
    *   **Objective:** Executes a series of transitions defined in `path` (a list of state IDs).
    *   **Behavior:** Steps through each transition using `step_transition`. Stops and returns an error if any transition is invalid.
    *   **Output:** Returns `{"ok": True, "payload": final_context}` or a structured error if a transition fails.

## Unit Tests (`engine/core/runtime/tests/test_state_machine_driver.py`)

A comprehensive suite of `pytest` unit tests will be developed to verify:
*   Successful loading of state machine definitions.
*   Correct initialization of runtime context.
*   Accurate `can_transition` logic for valid and invalid transitions.
*   Successful `step_transition` for valid paths, including updating context.
*   `step_transition` correctly identifying and failing on invalid transitions without changing state.
*   `run_scripted_path` successfully executing a sequence of valid transitions, including reaching `SHUTDOWN_ENGINE`.
*   `run_scripted_path` correctly failing and stopping on an invalid transition.
*   Debug logging integration: `_log_debug_event` is called when `debug=True`, and the driver remains functional if `debug_logger` is unavailable.

## Minimal State Machine Driver Documentation (`docs/design/runtime/minimal_state_machine_driver.md`)

This document details the responsibilities of the `state_machine_driver`, its interaction with external JSON definitions, and its strict adherence to not including gameplay logic.

## Validation and Integrity

A new validation script (`tests/validate_state_machine_driver_integration.py`) will perform integration tests to ensure:
*   `state_machine_driver.py` exists and implements all required functions.
*   The driver successfully loads the `game_loop_states.json` and `game_loop_transitions.json` (from TOWER-ENGINE-002).
*   Specific valid transitions (`BOOT_ENGINE` to `LOAD_CONTENT_PACK`, `ACTIVE_FLOOR_LOOP` to `RESOLVE_FLOOR_OUTCOME`) are recognized as valid.
*   A specific invalid transition (`BOOT_ENGINE` to `ACTIVE_FLOOR_LOOP`) is correctly identified as invalid and fails safely.
*   A full scripted path from `BOOT_ENGINE` to `SHUTDOWN_ENGINE` executes successfully.
*   Passing `debug=True` to driver functions does not break their core functionality.
*   No gameplay, combat, floor generation, multiplayer, rendering, or GPU-specific code is introduced in the driver.
