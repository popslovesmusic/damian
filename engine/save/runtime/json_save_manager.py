import os
import json
import jsonschema

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

def _log_debug_event(patch_id, system, severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        event = debug_logger.make_debug_event(patch_id, system, severity, event_type, message, context)
        # Assuming debug_logger.write_debug_event handles its own failures
        debug_logger.write_debug_event(event)
    elif not _debug_logger_available and debug_enabled:
        # Log a warning if debug is enabled but logger is not available
        print(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: {message}")

def create_structured_error(error_type, message, path="", debug=False):
    """Creates a structured error dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}

def load_json(path, debug=False):
    """
    Loads JSON from a file.
    Returns structured success with payload or structured error.
    """
    if not os.path.exists(path):
        return create_structured_error("FileNotFound", f"File not found at {path}", path, debug=debug)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "INFO", "successful_load", f"Successfully loaded JSON from {path}.", {"path": path}, debug)
        return create_structured_success(payload, path, debug=debug)
    except json.JSONDecodeError as e:
        return create_structured_error("InvalidJson", f"Invalid JSON in {path}: {e}", path, debug=debug)
    except Exception as e:
        return create_structured_error("FileReadError", f"Error reading file {path}: {e}", path, debug=debug)

def save_json(path, payload, debug=False):
    """
    Saves payload as JSON to a file.
    Creates parent directories if they don't exist.
    Returns structured success or structured error.
    """
    try:
        path = os.path.normpath(path)
        dirname = os.path.dirname(path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
            _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "DEBUG", "DirectoryCreated", f"Created directory {dirname}.", {"path": dirname}, debug)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "INFO", "successful_save", f"Successfully saved JSON to {path}.", {"path": path}, debug)
        return create_structured_success(None, path, debug=debug) # No payload for save success
    except TypeError as e:
        return create_structured_error("SerializationError", f"Payload not JSON serializable: {e}", path, debug=debug)
    except Exception as e:
        return create_structured_error("FileWriteError", f"Error writing file {path}: {e}", path, debug=debug)

def validate_json(payload, schema_path, debug=False):
    """
    Validates a JSON payload against a schema.
    Returns structured success or structured error.
    """
    if not os.path.exists(schema_path):
        return create_structured_error("SchemaNotFound", f"Schema file not found at {schema_path}", schema_path, debug=debug)

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except json.JSONDecodeError as e:
        return create_structured_error("InvalidSchema", f"Invalid JSON in schema file {schema_path}: {e}", schema_path, debug=debug)
    except Exception as e:
        return create_structured_error("SchemaReadError", f"Error reading schema file {schema_path}: {e}", schema_path, debug=debug)

    try:
        # Create a resolver that can find other schemas in the same directory
        # The base_uri needs to be a valid URI, so using file://
        base_uri = f"file://{os.path.abspath(os.path.dirname(schema_path)).replace(os.sep, '/')}/"
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        jsonschema.validate(instance=payload, schema=schema, resolver=resolver)
        _log_debug_event("TOWER-ENGINE-017", "json_save_manager", "INFO", "ValidationSuccess", "Payload validated successfully against schema.", {"schema_path": schema_path}, debug)
        return create_structured_success(True, schema_path, debug=debug) # Indicates validation success
    except jsonschema.ValidationError as e:
        return create_structured_error("SchemaValidationFailure", f"Payload failed schema validation: {e.message}", schema_path, debug=debug)
    except Exception as e:
        return create_structured_error("SchemaValidationError", f"An unexpected error occurred during validation: {e}", schema_path, debug=debug)

def load_validated_json(path, schema_path, debug=False):
    """
    Loads JSON from a file and validates it against a schema.
    Returns structured success with payload or structured error.
    """
    load_result = load_json(path, debug=debug)
    if not load_result["ok"]:
        return load_result
    
    payload = load_result["payload"]
    validation_result = validate_json(payload, schema_path, debug=debug)
    if not validation_result["ok"]:
        return validation_result
    
    return create_structured_success(payload, path, debug=debug)

def save_validated_json(path, payload, schema_path, debug=False):
    """
    Validates payload against a schema, then saves it to a file.
    Returns structured success or structured error.
    """
    validation_result = validate_json(payload, schema_path, debug=debug)
    if not validation_result["ok"]:
        return validation_result
    
    return save_json(path, payload, debug=debug)
