import json
import os
import datetime
import re
from engine.io.runtime import artifact_policy

def create_structured_error(error_type, message, path=""):
    """Creates a structured error dictionary for internal use."""
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload=None):
    """Creates a structured success dictionary for internal use."""
    return {"ok": True, "payload": payload}

def safe_context(context):
    """
    Redacts disallowed personal data fields from a context dictionary.
    This is a basic implementation; more robust PII redaction would be complex.
    """
    if not isinstance(context, dict):
        return context # Return as is if not a dictionary
    
    # Simple redaction for known PII fields
    redacted_context = context.copy()
    pii_fields = ["player_name", "email", "ip_address", "user_id", "login_id"]
    for field in pii_fields:
        if field in redacted_context:
            redacted_context[field] = "[REDACTED_PII]"
    
    # Remove potentially sensitive fields if they contain long strings that might be data dumps
    # This is a heuristic and can be refined.
    for key, value in redacted_context.items():
        if isinstance(value, str) and len(value) > 200: # Arbitrary length for long string
            redacted_context[key] = "[REDACTED_LONG_STRING]"
    
    return redacted_context

def make_debug_event(patch_id, system, severity, event_type, message, context=None):
    """
    Creates a structured debug event dictionary.
    Automatically adds timestamp and ensures safe context.
    """
    event = {
        "event_id": str(datetime.datetime.now().timestamp()), # Simple unique ID
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "patch_id": patch_id,
        "system": system,
        "severity": severity,
        "event_type": event_type,
        "message": message,
        "context": safe_context(context) if context else {},
        "safe_to_persist": True # Assume true unless explicitly marked otherwise
    }
    return event

def debug_enabled(config=None):
    """
    Checks if debugging is enabled.
    In a real system, this would read from a global config.
    For now, a simple placeholder.
    """
    # Debug log persistence is off by default; enable explicitly.
    if not artifact_policy.allow_debug_log_writes(default=False):
        return False
    if config and config.get("debug_logging_enabled") is False:
        return False
    return True

def write_debug_event(event, log_path='logs/debug/runtime_debug_log.jsonl'):
    """
    Writes a structured debug event to a local JSONL file.
    Creates parent directories if they don't exist.
    Does not raise on logging failure.
    Returns structured success or error.
    """
    if not debug_enabled(): # Don't write if debugging is not enabled
        return create_structured_success("Debugging not enabled.")

    try:
        dirname = os.path.dirname(log_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        
        # Append event as a JSON line
        with open(log_path, 'a', encoding='utf-8') as f:
            json.dump(event, f)
            f.write('\n') # Newline for JSONL format
        return create_structured_success("Event logged successfully.")
    except Exception as e:
        # Crucially, this function should not crash the caller
        return create_structured_error("LoggingFailure", f"Failed to write debug event to {log_path}: {e}")
