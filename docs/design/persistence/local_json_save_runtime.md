# Tower Engine Local JSON Save and Load Runtime Skeleton

This document outlines the design and implementation of the initial local JSON save/load runtime skeleton for the Tower Engine. This is the first practical runtime component, focusing on the safe and reliable persistence and retrieval of core game states using local JSON files, with robust schema validation.

## Core Principles

*   **Runtime Implementation Allowed:** This patch marks the transition from pure design contracts to actual executable code.
*   **Local JSON Only:** Persistence is strictly limited to local JSON files for this prototype phase. No database, cloud, or complex network save systems are introduced.
*   **Failure-Safe Behavior:** The save/load system must gracefully handle missing files, invalid JSON content, and schema validation failures, returning structured error messages without crashing the application.
*   **Schema Validation is King:** All loaded and saved data must adhere to their respective JSON schemas to maintain data integrity and prevent corruption.
*   **Minimal Scope:** Implementation is limited to basic save/load functionality and validation. No gameplay logic, rendering, or other complex runtime systems are included here.
*   **Structured Responses:** All save/load operations return a consistent structured dictionary indicating `ok` (boolean), `error_type` (string), `message` (string), and either `payload` (for success) or `path` (for error context).

## JSON Save Manager (`engine/save/runtime/json_save_manager.py`)

This Python module provides the core functions for interacting with local JSON save files.

### Required Functions:

*   `load_json(path)`:
    *   **Objective:** Reads a JSON file from the specified `path`.
    *   **Success:** Returns `{"ok": True, "payload": data}`.
    *   **Failure:** Returns `{"ok": False, "error_type": "FileNotFound" | "InvalidJson" | "FileReadError", "message": "...", "path": path}`.
*   `save_json(path, payload)`:
    *   **Objective:** Writes a Python dictionary (`payload`) to the specified `path` as JSON.
    *   **Behavior:** Automatically creates parent directories if they do not exist.
    *   **Success:** Returns `{"ok": True, "payload": None}`.
    *   **Failure:** Returns `{"ok": False, "error_type": "SerializationError" | "FileWriteError", "message": "...", "path": path}`.
*   `validate_json(payload, schema_path)`:
    *   **Objective:** Validates a given `payload` (Python dictionary) against a JSON schema located at `schema_path`.
    *   **Behavior:** Uses `jsonschema` library for validation, including a `RefResolver` to handle `$ref` in schemas.
    *   **Success:** Returns `{"ok": True, "payload": True}` (indicating validation success).
    *   **Failure:** Returns `{"ok": False, "error_type": "SchemaNotFound" | "InvalidSchema" | "SchemaReadError" | "SchemaValidationFailure" | "SchemaValidationError", "message": "...", "path": schema_path}`.
*   `load_validated_json(path, schema_path)`:
    *   **Objective:** Combines `load_json` and `validate_json`. Loads a file and then validates its content.
    *   **Success:** Returns `{"ok": True, "payload": data}`.
    *   **Failure:** Returns the error from either `load_json` or `validate_json`.
*   `save_validated_json(path, payload, schema_path)`:
    *   **Objective:** Combines `validate_json` and `save_json`. Validates the payload before saving it.
    *   **Success:** Returns `{"ok": True, "payload": None}`.
    *   **Failure:** Returns the error from `validate_json` or `save_json`.

## Unit Tests (`engine/save/runtime/tests/test_json_save_manager.py`)

A comprehensive suite of `pytest` unit tests will be developed to verify the correct functioning and failure-safe behavior of `json_save_manager.py`'s functions. This includes testing:
*   Successful loading and saving of valid JSON.
*   Handling of non-existent files.
*   Handling of malformed JSON content.
*   Creation of parent directories during save.
*   Successful and failed schema validation.

## Example Runtime Save Bundle (`saves/examples/example_runtime_save_bundle.json`)

This file provides a structured example of what a complete game save might look like in a single JSON file for testing purposes. It bundles `tower_state`, `player_progression_state`, and `domain_state` (using their respective initial example values from prior patches). This bundle is *not* a schema itself, but a payload that conceptually contains multiple sub-payloads which would each be validated against their own schemas.

## Local JSON Save Runtime Documentation (`docs/design/persistence/local_json_save_runtime.md`)

This document serves as design documentation for the local JSON save/load system, detailing its architecture, the purpose of each function, and how failure-safe behavior is achieved.

## Validation and Integrity

A new validation script (`tests/validate_json_save_runtime.py`) will perform integration tests to ensure:
*   All required functions are present in `json_save_manager.py`.
*   `load_json` and `save_json` demonstrate correct behavior for success and expected failure modes.
*   `validate_json` correctly handles valid and invalid payloads against a test schema.
*   `load_validated_json` successfully loads and validates existing schema-compliant data (e.g., `example_tower_state.json` against `tower_state.schema.json`).
*   `save_validated_json` correctly prevents saving of invalid data.
*   Crucially, no database, cloud, or network-related code is introduced within this scope.
