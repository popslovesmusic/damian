import os
import json
import datetime
import uuid
import hashlib
import sys

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import json_save_manager (assuming project root is in sys.path)
try:
    from engine.save.runtime import json_save_manager
    _json_save_manager_available = True
except ImportError:
    _json_save_manager_available = False

# Paths to existing schemas
# Assume these paths are relative to the project root (D:\projects\Damian)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_FLOOR_MEMORY_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
_FLOOR_IDENTITY_RULES_PATH = os.path.join(_PROJECT_ROOT, "engine/floor_generation/identity/floor_identity_preservation_rules.json")


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
        _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def make_floor_seed(content_pack_id, floor_id, domain_archetype, run_id='default'):
    """
    Generates a deterministic seed string for a floor.
    """
    seed_components = f"{content_pack_id}-{floor_id}-{domain_archetype}-{run_id}"
    return hashlib.sha256(seed_components.encode('utf-8')).hexdigest()

def make_floor_record(floor_id, content_pack_id='damian', domain_archetype='tower_domain', seed=None, debug=False):
    """
    Creates a minimal floor record for a given floor_id.
    """
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "INFO", "MakeFloorRecord", f"Creating floor record for floor_id: {floor_id}", {"floor_id": floor_id, "content_pack_id": content_pack_id, "domain_archetype": domain_archetype}, debug)

    if not isinstance(floor_id, int) or floor_id < 1:
        return create_structured_error("InvalidInput", f"floor_id must be an integer >= 1, got {floor_id}", debug=debug)
    if not content_pack_id:
        return create_structured_error("InvalidInput", "content_pack_id cannot be empty.", debug=debug)
    if not domain_archetype:
        return create_structured_error("InvalidInput", "domain_archetype cannot be empty.", debug=debug)

    if seed is None:
        layout_seed = make_floor_seed(content_pack_id, floor_id, domain_archetype)
    else:
        layout_seed = seed
    
    # Load identity anchors from the rules registry
    identity_rules_result = json_save_manager.load_json(_FLOOR_IDENTITY_RULES_PATH, debug=debug)
    identity_anchors_list = []
    if identity_rules_result["ok"]:
        for anchor in identity_rules_result["payload"].get("required_identity_anchors", []):
            identity_anchors_list.append(anchor["anchor_id"])
    else:
        _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "WARNING", "LoadIdentityRulesFailure", f"Could not load floor identity rules: {identity_rules_result['message']}", debug_enabled=debug)

    floor_record = {
        "floor_id": floor_id,
        "content_pack_id": content_pack_id,
        "domain_archetype": domain_archetype,
        "layout_seed": layout_seed,
        "seed_lineage": layout_seed, # Initial lineage is self
        "identity_anchors": identity_anchors_list,
        "mutation_level": 0,
        "active_mutations": [],
        "playability_status": "UNGENERATED_VALID"
    }
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "DEBUG", "FloorRecordCreated", f"Floor record created for floor_id: {floor_id}.", {"record": floor_record}, debug)
    return create_structured_success(floor_record, debug=debug)

def validate_floor_record(floor_record, debug=False):
    """
    Validates a floor record against the floor_memory.schema.json.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "DEBUG", "ValidateRecord", "Validating floor record.", {"record": floor_record}, debug)
    # The floor_memory.schema.json is designed to validate records that are part of floor_memory,
    # which implies it will accept the fields we generate here.
    validation_result = json_save_manager.validate_json(floor_record, _FLOOR_MEMORY_SCHEMA_PATH, debug=debug)
    if not validation_result["ok"]:
        _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "ERROR", "FloorRecordValidationFailure", f"Floor record failed schema validation: {validation_result['message']}", {"record": floor_record, "error": validation_result}, debug)
        return validation_result
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "INFO", "ValidationSuccess", "Floor record validated successfully.", debug_enabled=debug)
    return create_structured_success(True, debug=debug)


def make_floor_records(count=3, content_pack_id='damian', domain_archetype='tower_domain', run_id='default', debug=False):
    """
    Creates a list of floor records.
    """
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "INFO", "MakeFloorRecords", f"Creating {count} floor records.", {"count": count}, debug)
    floor_records = []
    for i in range(1, count + 1):
        record_result = make_floor_record(i, content_pack_id, domain_archetype, debug=debug)
        if not record_result["ok"]:
            return create_structured_error("FloorRecordCreationFailure", f"Failed to create floor record {i}: {record_result['message']}", debug=debug)
        floor_records.append(record_result["payload"])
    _log_debug_event("TOWER-ENGINE-023", "floor_record_builder", "INFO", "FloorRecordsCreated", f"Successfully created {count} floor records.", debug_enabled=debug)
    return create_structured_success(floor_records, debug=debug)
