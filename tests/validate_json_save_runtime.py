import sys
import os
import json
import jsonschema
import shutil

# Add project root to sys.path for module discovery
PROJECT_ROOT_FOR_IMPORT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT_FOR_IMPORT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_IMPORT)

from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches
# These paths are relative to the project root
BASE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TOWER_STATE_SCHEMA_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/save/schemas/tower_state.schema.json")
EXAMPLE_TOWER_STATE_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/save/examples/example_tower_state.json")

def create_structured_error(error_type, message, path=""):
    """Creates a structured error dictionary."""
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload):
    """Creates a structured success dictionary."""
    return {"ok": True, "payload": payload}

def run_json_save_runtime_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-017",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    json_save_manager_path = os.path.join(project_root, "engine/save/runtime/json_save_manager.py")

    # Check 1: json_save_manager.py exists
    json_manager_exists_check = {"check": "json_save_manager.py exists", "status": "PASS"}
    if not os.path.exists(json_save_manager_path):
        json_manager_exists_check["status"] = "FAIL"
        json_manager_exists_check["reason"] = f"File not found: {json_save_manager_path}"
    audit_results["checks"].append(json_manager_exists_check)
    if json_manager_exists_check["status"] == "FAIL":
        return audit_results # Cannot proceed without the file

    # Required save/load functions
    required_functions = [
        "load_json",
        "save_json",
        "validate_json",
        "load_validated_json",
        "save_validated_json"
    ]

    # Check 2: Required save/load functions exist
    functions_exist_check = {"check": "Required save/load functions exist", "status": "PASS"}
    for func_name in required_functions:
        if not hasattr(json_save_manager, func_name):
            functions_exist_check["status"] = "FAIL"
            functions_exist_check["reason"] = f"Function '{func_name}' is missing in json_save_manager.py."
            break
    audit_results["checks"].append(functions_exist_check)
    if functions_exist_check["status"] == "FAIL":
        return audit_results # Cannot proceed if functions are missing


    # Create a temporary directory for integration tests
    TEMP_TEST_DIR = os.path.join(project_root, "temp_runtime_tests")
    if os.path.exists(TEMP_TEST_DIR):
        shutil.rmtree(TEMP_TEST_DIR)
    os.makedirs(TEMP_TEST_DIR)

    # Re-import json_save_manager to ensure latest code is used after potential previous file writing
    import importlib
    importlib.reload(json_save_manager)

    # --- Integration Tests (mimicking unit test checks but in validation script) ---

    # Test load_json
    # Success
    load_json_success_check = {"check": "load_json returns structured success for valid JSON", "status": "PASS"}
    test_load_path = os.path.join(TEMP_TEST_DIR, "valid_load.json")
    test_load_data = {"test": "data", "id": 1}
    with open(test_load_path, 'w') as f:
        json.dump(test_load_data, f)
    result = json_save_manager.load_json(test_load_path)
    if not (result["ok"] is True and result["payload"] == test_load_data):
        load_json_success_check["status"] = "FAIL"
        load_json_success_check["reason"] = f"load_json failed success test: {result}"
    audit_results["checks"].append(load_json_success_check)

    # Missing file
    load_json_missing_check = {"check": "load_json returns structured error for missing file", "status": "PASS"}
    result = json_save_manager.load_json(os.path.join(TEMP_TEST_DIR, "non_existent.json"))
    if not (result["ok"] is False and result["error_type"] == "FileNotFound"):
        load_json_missing_check["status"] = "FAIL"
        load_json_missing_check["reason"] = f"load_json failed missing file test: {result}"
    audit_results["checks"].append(load_json_missing_check)

    # Invalid JSON
    load_json_invalid_check = {"check": "load_json returns structured error for invalid JSON", "status": "PASS"}
    test_invalid_path = os.path.join(TEMP_TEST_DIR, "invalid_json.json")
    with open(test_invalid_path, 'w') as f:
        f.write("{broken json}")
    result = json_save_manager.load_json(test_invalid_path)
    if not (result["ok"] is False and result["error_type"] == "InvalidJson"):
        load_json_invalid_check["status"] = "FAIL"
        load_json_invalid_check["reason"] = f"load_json failed invalid JSON test: {result}"
    audit_results["checks"].append(load_json_invalid_check)

    # Test save_json
    # Create parent directories
    save_json_mkdirs_check = {"check": "save_json creates parent directories when needed", "status": "PASS"}
    test_save_path_deep = os.path.join(TEMP_TEST_DIR, "new_dir", "deep_nested", "save.json")
    test_save_data = {"hello": "world"}
    result = json_save_manager.save_json(test_save_path_deep, test_save_data)
    if not (result["ok"] is True and os.path.exists(test_save_path_deep)):
        save_json_mkdirs_check["status"] = "FAIL"
        save_json_mkdirs_check["reason"] = f"save_json failed mkdir test: {result}"
    audit_results["checks"].append(save_json_mkdirs_check)


    # Test validate_json
    # Valid payload
    validate_json_valid_check = {"check": "validate_json returns structured success for valid payload", "status": "PASS"}
    test_payload_valid = {"name": "Audit", "value": 100}
    test_schema_for_validate = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "value": {"type": "integer"}},
        "required": ["name"]
    }
    test_schema_path_for_validate = os.path.join(TEMP_TEST_DIR, "validate_schema.json")
    with open(test_schema_path_for_validate, 'w') as f:
        json.dump(test_schema_for_validate, f)
    result = json_save_manager.validate_json(test_payload_valid, test_schema_path_for_validate)
    if not (result["ok"] is True):
        validate_json_valid_check["status"] = "FAIL"
        validate_json_valid_check["reason"] = f"validate_json failed valid payload test: {result}"
    audit_results["checks"].append(validate_json_valid_check)

    # Invalid payload
    validate_json_invalid_check = {"check": "validate_json returns structured error for invalid payload", "status": "PASS"}
    test_payload_invalid = {"name": "Audit", "value": "one hundred"} # value should be int
    result = json_save_manager.validate_json(test_payload_invalid, test_schema_path_for_validate)
    if not (result["ok"] is False and result["error_type"] == "SchemaValidationFailure"):
        validate_json_invalid_check["status"] = "FAIL"
        validate_json_invalid_check["reason"] = f"validate_json failed invalid payload test: {result}"
    audit_results["checks"].append(validate_json_invalid_check)


    # Test load_validated_json against a known schema/example
    load_validated_integration_check = {"check": "load_validated_json works against tower_state.schema.json using example_tower_state.json", "status": "PASS"}
    try:
        result = json_save_manager.load_validated_json(EXAMPLE_TOWER_STATE_PATH, TOWER_STATE_SCHEMA_PATH)
        if not (result["ok"] is True and result["payload"] is not None):
            load_validated_integration_check["status"] = "FAIL"
            load_validated_integration_check["reason"] = f"load_validated_json failed for tower_state example: {result}"
    except Exception as e:
        load_validated_integration_check["status"] = "FAIL"
        load_validated_integration_check["reason"] = f"load_validated_json raised exception for tower_state example: {e}"
    audit_results["checks"].append(load_validated_integration_check)

    # Test save_validated_json with invalid payload
    save_validated_invalid_check = {"check": "save_validated_json rejects invalid payload safely", "status": "PASS"}
    test_save_validated_path = os.path.join(TEMP_TEST_DIR, "invalid_payload_not_saved.json")
    test_invalid_payload_for_save = {"id": "invalid", "current_floor": "one"} # current_floor should be integer
    result = json_save_manager.save_validated_json(test_save_validated_path, test_invalid_payload_for_save, TOWER_STATE_SCHEMA_PATH)
    if not (result["ok"] is False and result["error_type"] == "SchemaValidationFailure" and not os.path.exists(test_save_validated_path)):
        save_validated_invalid_check["status"] = "FAIL"
        save_validated_invalid_check["reason"] = f"save_validated_json failed to reject invalid payload or saved it: {result}"
    audit_results["checks"].append(save_validated_invalid_check)


    # Check: No database/cloud/network code is introduced (conceptual, manual check)
    no_external_deps_check = {"check": "No database/cloud/network code is introduced", "status": "PASS"}
    # This check relies on code review for actual implementation, but for automated checks
    # we can try to look for obvious keywords. For now, it passes by design expectation.
    # A more robust check would involve static analysis of the python file.
    with open(json_save_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if "sqlite" in content or "mongo" in content or "http" in content or "socket" in content:
            no_external_deps_check["status"] = "FAIL"
            no_external_deps_check["reason"] = "Detected potential external dependency keywords in json_save_manager.py."
    audit_results["checks"].append(no_external_deps_check)

    # Clean up temporary test directory
    shutil.rmtree(TEMP_TEST_DIR)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_017_json_save_runtime_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_017_json_save_runtime_result.json")

    # Add verbose printing before writing
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Project Root: {project_root}")
    print(f"Attempting to write audit to: {audit_file_path}")
    try:
        with open(audit_file_path, 'w') as f:
            json.dump(audit_results, f, indent=2)
        print(f"Successfully wrote audit to {audit_file_path}")
    except Exception as e:
        print(f"ERROR: Failed to write audit file {audit_file_path}: {e}")

    print(f"Attempting to write validation results to: {result_file_path}")
    try:
        with open(result_file_path, 'w') as f:
            json.dump({"verdict": audit_results["verdict"]}, f, indent=2)
        print(f"Successfully wrote validation results to {result_file_path}")
    except Exception as e:
        print(f"ERROR: Failed to write result file {result_file_path}: {e}")

    print(f"Audit results written to {audit_file_path}")
    print(f"Validation results written to {result_file_path}")
    return audit_results

if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema library not found. Please install it: pip install jsonschema")
        exit(1)
    
    # Ensure pytest is installed for unit tests
    try:
        import pytest
    except ImportError:
        print("pytest library not found. Please install it: pip install pytest")
        exit(1)

    # Run the audit (which includes integration-like tests)
    audit = run_json_save_runtime_audit()
    print(json.dumps(audit, indent=2))
