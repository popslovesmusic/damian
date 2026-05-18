import os
import json
import jsonschema
import shutil
import datetime
import sys

# Add project root to sys.path for module discovery
PROJECT_ROOT_FOR_IMPORT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT_FOR_IMPORT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_IMPORT)

from engine.debug.runtime import debug_logger

# Paths to the current patch's files. BASE_PROJECT_ROOT is now the root of the Damian project.
BASE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEBUG_SCHEMA_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/debug/contracts/debug_event.schema.json")
EXAMPLE_DEBUG_EVENT_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/debug/contracts/example_debug_event.json")
DEBUG_LOGGER_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/debug/runtime/debug_logger.py")


def run_runtime_debugging_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-017A",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    debug_schema_data = {}
    example_debug_event_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    debug_schema_data = load_json_file(DEBUG_SCHEMA_PATH, "debug_event.schema.json")
    example_debug_event_data = load_json_file(EXAMPLE_DEBUG_EVENT_PATH, "example_debug_event.json")

    if not all([debug_schema_data, example_debug_event_data]):
        # The audit_results will already contain the failed load checks
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.abspath(os.path.dirname(DEBUG_SCHEMA_PATH)).replace(os.sep, '/')}/",
        referrer=debug_schema_data
    )

    # Check 1: debug_logger.py exists
    debug_logger_exists_check = {"check": "debug_logger.py exists", "status": "PASS"}
    if not os.path.exists(DEBUG_LOGGER_PATH):
        debug_logger_exists_check["status"] = "FAIL"
        debug_logger_exists_check["reason"] = f"File not found: {DEBUG_LOGGER_PATH}"
    audit_results["checks"].append(debug_logger_exists_check)

    # Check 2: debug_event.schema.json exists (handled by load_json_file)
    audit_results["checks"].append({"check": "debug_event.schema.json exists", "status": "PASS"})

    # Check 3: example_debug_event.json validates against schema
    example_validation_check = {"check": "example_debug_event.json validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_debug_event_data, schema=debug_schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Required functions from debug_logger.py
    required_functions = [
        "make_debug_event",
        "write_debug_event",
        "debug_enabled",
        "safe_context"
    ]

    # Check presence of functions
    functions_exist_check = {"check": "Required debug_logger functions exist", "status": "PASS"}
    for func_name in required_functions:
        if not hasattr(debug_logger, func_name):
            functions_exist_check["status"] = "FAIL"
            functions_exist_check["reason"] = f"Function '{func_name}' is missing in debug_logger.py."
            break
    audit_results["checks"].append(functions_exist_check)
    if functions_exist_check["status"] == "FAIL":
        # Cannot proceed with behavioral checks if functions are missing
        return audit_results


    # Create a temporary directory for logging tests
    TEMP_LOG_DIR = os.path.join(project_root, "temp_debug_logs")
    if os.path.exists(TEMP_LOG_DIR):
        shutil.rmtree(TEMP_LOG_DIR)
    os.makedirs(TEMP_LOG_DIR)
    test_log_file = os.path.join(TEMP_LOG_DIR, "test_log.jsonl")
    deep_log_file = os.path.join(TEMP_LOG_DIR, "deep", "nested", "test_log_deep.jsonl")


    # Check 4: debug_logger writes JSONL locally
    writes_jsonl_check = {"check": "debug_logger writes JSONL locally", "status": "PASS"}
    test_event = debug_logger.make_debug_event("TEST-001", "Audit", "DEBUG", "TestWrite", "Test message for JSONL.")
    write_result = debug_logger.write_debug_event(test_event, test_log_file)
    if not (write_result["ok"] and os.path.exists(test_log_file)):
        writes_jsonl_check["status"] = "FAIL"
        writes_jsonl_check["reason"] = f"Failed to write event to JSONL file: {write_result}"
    else:
        try:
            with open(test_log_file, 'r') as f:
                line = f.readline()
                loaded_event = json.loads(line)
                if loaded_event != test_event:
                    writes_jsonl_check["status"] = "FAIL"
                    writes_jsonl_check["reason"] = "Written event does not match original."
        except Exception as e:
            writes_jsonl_check["status"] = "FAIL"
            writes_jsonl_check["reason"] = f"Failed to read/parse written JSONL: {e}"
    audit_results["checks"].append(writes_jsonl_check)

    # Check 5: debug logger creates parent directories
    creates_dirs_check = {"check": "debug logger creates parent directories", "status": "PASS"}
    deep_test_event = debug_logger.make_debug_event("TEST-001", "Audit", "INFO", "DeepWrite", "Deep path test.")
    write_result_deep = debug_logger.write_debug_event(deep_test_event, deep_log_file)
    if not (write_result_deep["ok"] and os.path.exists(deep_log_file)):
        creates_dirs_check["status"] = "FAIL"
        creates_dirs_check["reason"] = f"Failed to write event to deep path file: {write_result_deep}"
    audit_results["checks"].append(creates_dirs_check)

    # Check 6: debug logger does not crash caller on logging failure
    no_crash_on_failure_check = {"check": "debug logger does not crash caller on logging failure", "status": "PASS"}
    # Simulate a write failure (e.g., read-only directory)
    read_only_dir = os.path.join(TEMP_LOG_DIR, "read_only")
    os.makedirs(read_only_dir)
    # On Windows, os.chmod is tricky; best to simulate by passing an invalid path for open()
    invalid_path_log = os.path.join(read_only_dir, "non_existent_dir/log.jsonl") # This path will fail os.makedirs if not exist_ok
    
    # Temporarily remove exist_ok=True from os.makedirs to force an error for testing
    original_makedirs = os.makedirs
    def mock_makedirs_failure(*args, **kwargs):
        raise OSError("Simulated permission error")
    
    try:
        with patch('os.makedirs', side_effect=mock_makedirs_failure):
            fail_event = debug_logger.make_debug_event("TEST-001", "Audit", "ERROR", "SimulatedFailure", "This should fail silently.")
            result_of_failure = debug_logger.write_debug_event(fail_event, test_log_file)
            if result_of_failure["ok"] or result_of_failure["error_type"] != "LoggingFailure":
                no_crash_on_failure_check["status"] = "FAIL"
                no_crash_on_failure_check["reason"] = f"write_debug_event did not return expected error on simulated failure: {result_of_failure}"
    except Exception as e:
        no_crash_on_failure_check["status"] = "FAIL"
        no_crash_on_failure_check["reason"] = f"write_debug_event crashed on simulated failure: {e}"
    finally:
        os.makedirs = original_makedirs # Restore original function
    audit_results["checks"].append(no_crash_on_failure_check)


    # Check 7: debugging is optional
    debugging_optional_check = {"check": "debugging is optional", "status": "PASS"}
    # Test debug_enabled with config
    test_config_enabled = {"debug_logging_enabled": True}
    test_config_disabled = {"debug_logging_enabled": False}
    if not debug_logger.debug_enabled(test_config_enabled):
        debugging_optional_check["status"] = "FAIL"
        debugging_optional_check["reason"] = "debug_enabled not returning True when explicitly enabled."
    if debugging_optional_check["status"] == "PASS" and debug_logger.debug_enabled(test_config_disabled):
        debugging_optional_check["status"] = "FAIL"
        debugging_optional_check["reason"] = "debug_enabled not returning False when explicitly disabled."
    audit_results["checks"].append(debugging_optional_check)

    # Check 8: debugging does not require network or cloud
    no_network_cloud_check = {"check": "debugging does not require network or cloud", "status": "PASS"}
    # This check relies on code review for actual implementation, but for automated checks
    # we can try to look for obvious keywords.
    with open(DEBUG_LOGGER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        if "http" in content or "https" in content or "ftp" in content or "s3" in content or "azure" in content or "gcloud" in content:
            no_network_cloud_check["status"] = "FAIL"
            no_network_cloud_check["reason"] = "Detected potential network/cloud keywords in debug_logger.py."
    audit_results["checks"].append(no_network_cloud_check)

    # Clean up temporary test directory
    shutil.rmtree(TEMP_LOG_DIR)


    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_017a_debug_boundary_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_017a_debug_boundary_result.json")

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
    
    # Removed pytest check since it's not needed for this script, but for unit tests
    # Ensure any mock setup for os.makedirs is clean, otherwise, tests might fail unexpectedly
    audit = run_runtime_debugging_audit()
    print(json.dumps(audit, indent=2))
