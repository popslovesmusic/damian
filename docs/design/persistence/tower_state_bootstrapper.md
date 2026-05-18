# Tower Engine Minimal Tower State Bootstrapper

This document defines the implementation and behavior of the `tower_state_bootstrapper`, a critical runtime component responsible for ensuring a valid Tower State is available at application startup. This module leverages the `json_save_manager` (from TOWER-ENGINE-017) and integrates debug logging (from TOWER-ENGINE-017A) to provide robust and transparent persistence.

## Core Principles

*   **Runtime Implementation:** This patch involves writing functional code to manage the Tower State.
*   **Local JSON Persistence:** All interactions with saved data are strictly through local JSON files, validated against `tower_state.schema.json` (from TOWER-ENGINE-003).
*   **Debug Hooks Integrated:** Operations are instrumented with optional debug logging, providing structured diagnostics.
*   **Default State Creation:** If no valid save file is found, a default, minimal Tower State can be created and persisted, allowing for new game starts.
*   **Failure-Safe Operations:** The bootstrapper is designed to gracefully handle scenarios like missing save files, corrupted JSON, or schema validation failures, returning structured errors without crashing.
*   **No Gameplay Logic:** This module focuses exclusively on persistence management for the Tower State. No combat, floor generation, multiplayer, or rendering logic is present.

## Tower State Bootstrapper (`engine/save/bootstrap/tower_state_bootstrapper.py`)

This Python module provides functions to create, load, and save the core Tower State.

### Required Functions:

*   `make_default_tower_state(content_pack_id='damian', engine_version='0.0.1')`:
    *   **Objective:** Generates a new, minimal, and valid Tower State dictionary.
    *   **Content:** Sets `current_floor=1`, `highest_floor_reached=1`, `total_runs=0`, `total_deaths=0`, `last_outcome="BOOTSTRAP"`, and an ISO-formatted `updated_at` timestamp.
    *   **Output:** Returns a dictionary conforming to `tower_state.schema.json`.
*   `load_tower_state(save_path, schema_path=_TOWER_STATE_SCHEMA_PATH, debug=False)`:
    *   **Objective:** Loads a Tower State from `save_path` and validates it against `schema_path`.
    *   **Behavior:** Uses `json_save_manager.load_validated_json`. Logs debug events for load success/failure.
    *   **Output:** Returns `{"ok": True, "payload": tower_state}` or a structured error.
*   `save_tower_state(save_path, tower_state, schema_path=_TOWER_STATE_SCHEMA_PATH, debug=False)`:
    *   **Objective:** Saves a `tower_state` dictionary to `save_path` after validation.
    *   **Behavior:** Uses `json_save_manager.save_validated_json`. Logs debug events for save success/failure.
    *   **Output:** Returns `{"ok": True, "payload": None}` or a structured error.
*   `bootstrap_tower_state(save_path, schema_path=_TOWER_STATE_SCHEMA_PATH, create_if_missing=True, debug=False)`:
    *   **Objective:** The primary entry point for obtaining a valid Tower State.
    *   **Behavior:**
        1.  Attempts to `load_tower_state` from `save_path`.
        2.  If load succeeds and state is valid, returns the loaded state.
        3.  If `save_path` is not found and `create_if_missing` is `True`, it calls `make_default_tower_state` and then `save_tower_state`.
        4.  If `save_path` is not found and `create_if_missing` is `False`, or if an existing save is invalid, it returns a structured error.
    *   **Output:** Returns `{"ok": True, "payload": tower_state}` (loaded or default) or a structured error.

## Unit Tests (`engine/save/bootstrap/tests/test_tower_state_bootstrapper.py`)

A comprehensive `pytest` suite verifies:
*   `make_default_tower_state` creates a valid state (including current_floor=1, highest_floor_reached=1, last_outcome="BOOTSTRAP").
*   `load_tower_state` correctly loads valid saves and fails safely for missing files, invalid JSON, and invalid schema data.
*   `save_tower_state` correctly saves valid data and rejects invalid data.
*   `bootstrap_tower_state` successfully creates a default state when missing (and `create_if_missing=True`).
*   `bootstrap_tower_state` returns `FileNotFound` error when missing (and `create_if_missing=False`).
*   `bootstrap_tower_state` loads valid existing saves.
*   `bootstrap_tower_state` returns `SchemaValidationFailure` for invalid existing saves.
*   Debug logging integration: calls to `_log_debug_event` occur when `debug=True`, and the bootstrapper remains functional if `debug_logger` is unavailable.

## Tower State Bootstrapper Documentation (`docs/design/persistence/tower_state_bootstrapper.md`)

This document details the responsibilities of the `tower_state_bootstrapper`, its interaction with `json_save_manager` and `debug_logger`, and its strict adherence to safe and structured state management.
