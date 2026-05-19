# Tower Engine Minimal Player Progression Bootstrapper

This document defines the implementation and behavior of the `player_progression_bootstrapper`, a critical runtime component responsible for ensuring a valid player progression state is available at application startup. This module leverages the `json_save_manager` (from TOWER-ENGINE-017) and integrates debug logging (from TOWER-ENGINE-017A) to provide robust and transparent persistence.

## Core Principles

*   **Runtime Implementation:** This patch involves writing functional code to manage the Player Progression State.
*   **Local JSON Persistence:** All interactions with saved data are strictly through local JSON files, validated against `player_progression_state.schema.json` (from TOWER-ENGINE-008).
*   **Debug Hooks Integrated:** Operations are instrumented with optional debug logging, providing structured diagnostics.
*   **Default State Creation:** If no valid save file is found, a default, minimal player progression state can be created and persisted, allowing for new player starts.
*   **Failure-Safe Operations:** The bootstrapper is designed to gracefully handle scenarios like missing save files, corrupted JSON, or schema validation failures, returning structured errors without crashing.
*   **Bounded Progression Adherence:** The bootstrapper ensures that default and loaded progression states respect the anti-god-mode principles defined in TOWER-ENGINE-008, specifically that `forbidden_flags` are always `false`.
*   **No Gameplay Logic:** This module focuses exclusively on persistence management for the Player Progression State. No combat, skill tree, itemization, multiplayer, or rendering logic is present.

## Player Progression Bootstrapper (`engine/player/bootstrap/player_progression_bootstrapper.py`)

This Python module provides functions to create, load, and save the core Player Progression State.

### Required Functions:

*   `make_default_player_progression(player_id='player_default_001', profile_id='profile_default_001', content_pack_id='damian')`:
    *   **Objective:** Generates a new, minimal, and valid player progression state dictionary.
    *   **Content:** Sets `level=1`, `highest_floor_reached=1`, `stats` to initial values, `residue_pressure` to `0.0`, and all `forbidden_flags` to `false`. Uses generated unique IDs for `player_id` and `profile_id`.
    *   **Output:** Returns a dictionary conforming to `player_progression_state.schema.json`.
*   `load_player_progression(save_path, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, debug=False)`:
    *   **Objective:** Loads a player progression state from `save_path` and validates it.
    *   **Behavior:** Uses `json_save_manager.load_validated_json`. Logs debug events for load success/failure.
    *   **Output:** Returns `{"ok": True, "payload": player_progression}` or a structured error.
*   `save_player_progression(save_path, player_progression, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, debug=False)`:
    *   **Objective:** Saves a `player_progression` dictionary to `save_path` after validation.
    *   **Behavior:** Uses `json_save_manager.save_validated_json`. Logs debug events for save success/failure.
    *   **Output:** Returns `{"ok": True, "payload": None}` or a structured error.
*   `bootstrap_player_progression(save_path, schema_path=_PLAYER_PROGRESSION_SCHEMA_PATH, create_if_missing=True, debug=False)`:
    *   **Objective:** The primary entry point for obtaining a valid Player Progression State.
    *   **Behavior:**
        1.  Attempts to `load_player_progression` from `save_path`.
        2.  If load succeeds and state is valid, returns the loaded state.
        3.  If `save_path` is not found and `create_if_missing` is `True`, it calls `make_default_player_progression` and then `save_player_progression`.
        4.  If `save_path` is not found and `create_if_missing` is `False`, or if an existing save is invalid, it returns a structured error.
    *   **Output:** Returns `{"ok": True, "payload": player_progression}` (loaded or default) or a structured error.

## Unit Tests (`engine/player/bootstrap/tests/test_player_progression_bootstrapper.py`)

A comprehensive `pytest` suite verifies:
*   `make_default_player_progression` creates a valid state (including `level=1`, `highest_floor_reached=1`, and `forbidden_flags` all `false`).
*   `load_player_progression` correctly loads valid saves and fails safely for missing files, invalid JSON, and invalid schema data.
*   `save_player_progression` correctly saves valid data and rejects invalid data.
*   `bootstrap_player_progression` successfully creates a default state when missing (and `create_if_missing=True`).
*   `bootstrap_player_progression` returns `FileNotFound` error when missing (and `create_if_missing=False`).
*   `bootstrap_player_progression` loads valid existing saves.
*   `bootstrap_player_progression` returns `SchemaValidationFailure` for invalid existing saves.
*   Debug logging integration: calls to `_log_debug_event` occur when `debug=True`, and the bootstrapper remains functional if `debug_logger` is unavailable.

## Player Progression Bootstrapper Documentation (`docs/design/player/player_progression_bootstrapper.md`)

This document details the responsibilities of the `player_progression_bootstrapper`, its interaction with `json_save_manager` and `debug_logger`, and its strict adherence to safe and structured state management while enforcing bounded progression rules.
