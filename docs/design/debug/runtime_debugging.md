# Tower Engine Runtime Debug Logging and Diagnostic Boundary

This document defines the architecture for a lightweight, optional debug and diagnostic logging system within the Tower Engine. Its primary purpose is to provide traceable insights into runtime behavior and failures without altering core gameplay logic. This system is crucial for development, testing, and post-mortem analysis.

## Core Principles

*   **Debugging Must Be Optional:** The debugging system should be configurable and can be entirely disabled in production builds to avoid performance overhead and information leakage.
*   **No Gameplay State Change:** The act of logging or debugging must not introduce side effects that alter game state or gameplay behavior. It is purely an observational mechanism.
*   **Local-Only Logs:** Debug logs are strictly local to the running instance of the engine. No cloud logging, network logging, or remote telemetry is permitted within this system's scope for this prototype phase.
*   **No Personal Data Logging:** Player-identifiable information (PII) or other sensitive data must be explicitly redacted or excluded from logs.
*   **Structured Errors Required:** Error messages and diagnostic events must be structured for programmatic parsing and analysis, enabling automated tooling to identify patterns and root causes.
*   **Fail-Safe Logging:** The logging system itself must be resilient. Failures in the logging mechanism (e.g., disk full, invalid path) should not cause the main application to crash or malfunction.

## Debug Logger (`engine/debug/runtime/debug_logger.py`)

This Python module provides the core functions for generating and persisting structured debug events.

### Required Functions:

*   `make_debug_event(patch_id, system, severity, event_type, message, context=None)`:
    *   **Objective:** Constructs a structured debug event dictionary.
    *   **Behavior:** Automatically adds `timestamp` and ensures `safe_context` (redacts PII).
    *   **Output:** Returns a dictionary conforming to `debug_event.schema.json`.
*   `write_debug_event(event, log_path='logs/debug/runtime_debug_log.jsonl')`:
    *   **Objective:** Appends a structured debug event to a local JSONL (JSON Lines) file.
    *   **Behavior:**
        *   Creates parent directories for `log_path` if they don't exist.
        *   Does *not* raise exceptions on logging failures (e.g., file write errors); instead, returns a structured error response.
        *   Only writes the event if `debug_enabled()` returns `True`.
    *   **Output:** Returns `{"ok": True, "payload": "..."}` for success or `{"ok": False, "error_type": "LoggingFailure", "message": "...", "path": log_path}` for failure.
*   `debug_enabled(config=None)`:
    *   **Objective:** Checks if debug logging is currently active.
    *   **Behavior:** For this prototype, it defaults to `True` unless a provided `config` explicitly disables it. In a full engine, this would query a global configuration.
*   `safe_context(context)`:
    *   **Objective:** Takes a context dictionary and redacts any identified sensitive (PII) fields.
    *   **Behavior:** Currently performs basic redaction of `player_name`, `email`, `ip_address`, `user_id`, `login_id`, and redacts overly long string values heuristically.

### Logging Format:

*   Events are written in JSON Lines (JSONL) format: each line in the log file is a valid JSON object, allowing for easy parsing.

## Debug Event Contract (`engine/debug/contracts/debug_event.schema.json`)

This JSON Schema validates the structure of individual debug event records, ensuring consistency and parsability.

### Key Fields:

*   `event_id`, `timestamp`, `patch_id`, `system`, `severity`, `event_type`, `message`: Standard log event metadata.
*   `context`: An object containing additional details, with sensitive information redacted.
*   `safe_to_persist`: A boolean flag indicating if the event is safe for long-term storage or sharing.

## Example Debug Event (`engine/debug/contracts/example_debug_event.json`)

This file provides a concrete example of a valid debug event, illustrating a `FileWriteSuccess` from the `json_save_manager` system.

## Integration Note for `json_save_manager.py` (TOWER-ENGINE-017)

The `json_save_manager.py` module (from patch TOWER-ENGINE-017) should be updated to incorporate `debug_logger.py`.
*   It `may import debug_logger`.
*   It `must remain functional if debug_logger import fails` (robustness against a broken logger).
*   It `should log missing_file, invalid_json, schema_validation_failure, successful_save, successful_load` using `debug_logger` when `debug_enabled` is `True`.

## Validation and Integrity

The validation script (`tests/validate_runtime_debugging.py`) ensures:
*   `debug_logger.py` exists and implements the required functions.
*   `debug_event.schema.json` is a valid JSON Schema.
*   `example_debug_event.json` validates successfully against the schema.
*   `debug_logger` correctly writes JSONL to a local file.
*   `debug_logger` creates necessary parent directories for log files.
*   `debug_logger` does not crash the caller when logging fails (e.g., due to file system issues).
*   `debug_enabled` functionality is present.
*   No network or cloud logging attempts are present in the `debug_logger.py` code.
