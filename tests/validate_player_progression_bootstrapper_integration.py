import os
import json
import jsonschema
import shutil
import sys
from unittest.mock import patch

# Add project root to sys.path for module discovery
PROJECT_ROOT_FOR_IMPORT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT_FOR_IMPORT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_IMPORT)

from engine.player.bootstrap import player_progression_bootstrapper
from engine.save.runtime import json_save_manager # This will handle its own debug_logger import

# Paths to existing schemas and example data from previous patches (relative to project root)
BASE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLAYER_PROGRESSION_SCHEMA_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/player/contracts/player_progression_state.schema.json")
EXAMPLE_PLAYER_PROGRESSION_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/player/contracts/example_player_progression_state.json")

def run_player_progression_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-020",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    bootstrapper_path = os.path.join(project_root, "engine/player/bootstrap/player_progression_bootstrapper.py")

    # Check 1: player_progression_bootstrapper.py exists
    bootstrapper_exists_check = {"check": "player_progression_bootstrapper.py exists", "status": "PASS"}
    if not os.path.exists(bootstrapper_path):
        bootstrapper_exists_check["status"] = "FAIL"
        bootstrapper_exists_check["reason"] = f"File not found: {bootstrapper_path}"
    audit_results["checks"].append(bootstrapper_exists_check)
    if bootstrapper_exists_check["status"] == "FAIL":
        return audit_results

    # Required bootstrapper functions
    required_functions = [
        "make_default_player_progression",
        "bootstrap_player_progression",
        "load_player_progression",
        "save_player_progression"
    ]

    # Check 2: Required bootstrapper functions exist
    functions_exist_check = {"check": "Required bootstrapper functions exist", "status": "PASS"}
    for func_name in required_functions:
        if not hasattr(player_progression_bootstrapper, func_name):
            functions_exist_check["status"] = "FAIL"
            functions_exist_check["reason"] = f"Function '{func_name}' is missing in player_progression_bootstrapper.py."
            break
    audit_results["checks"].append(functions_exist_check)
    if functions_exist_check["status"] == "FAIL":
        return audit_results

    # Load player progression schema for validation
    schema_load_result = json_save_manager.load_json(PLAYER_PROGRESSION_SCHEMA_PATH)
    if not schema_load_result["ok"]:
        audit_results["checks"].append({"check": "Load player_progression_state.schema.json", "status": "FAIL", "reason": schema_load_result["message"]})
        return audit_results
    player_progression_schema = schema_load_result["payload"]


    # Check 3: Default player progression validates against player_progression_state.schema.json
    default_state_validation_check = {"check": "Default player progression validates against player_progression_state.schema.json", "status": "PASS"}
    default_progression = player_progression_bootstrapper.make_default_player_progression()
    try:
        # Use json_save_manager's validate_json for consistency
        validation_result = json_save_manager.validate_json(default_progression, PLAYER_PROGRESSION_SCHEMA_PATH)
        if not validation_result["ok"]:
            default_state_validation_check["status"] = "FAIL"
            default_state_validation_check["reason"] = f"Default progression failed schema validation: {validation_result.get('message')}"
    except Exception as e:
        default_state_validation_check["status"] = "FAIL"
        default_state_validation_check["reason"] = f"Error during default progression validation: {e}"
    audit_results["checks"].append(default_state_validation_check)

    # Check 4: Default player level = 1
    default_level_check = {"check": "Default player level = 1", "status": "PASS"}
    if default_progression.get("level") != 1:
        default_level_check["status"] = "FAIL"
        default_level_check["reason"] = f"Default progression level is {default_progression.get('level')}, expected 1."
    audit_results["checks"].append(default_level_check)

    # Check 5: Default highest_floor_reached = 1
    default_highest_floor_check = {"check": "Default highest_floor_reached = 1", "status": "PASS"}
    if default_progression.get("highest_floor_reached") != 1:
        default_highest_floor_check["status"] = "FAIL"
        default_highest_floor_check["reason"] = f"Default highest_floor_reached is {default_progression.get('highest_floor_reached')}, expected 1."
    audit_results["checks"].append(default_highest_floor_check)

    # Check 6: Default stats are positive or non-negative as required by schema
    default_stats_check = {"check": "Default stats are positive or non-negative as required by schema", "status": "PASS"}
    stats = default_progression.get("stats", {})
    if not (stats.get("health", 0) > 0 and stats.get("damage", 0) >= 0 and stats.get("defense", 0) >= 0 and stats.get("speed", 0) > 0 and stats.get("recovery", 0) >= 0):
        default_stats_check["status"] = "FAIL"
        default_stats_check["reason"] = f"Default stats do not meet positive/non-negative requirements: {stats}"
    audit_results["checks"].append(default_stats_check)


    # Check 7: Default residue pressure values are all 0.0
    default_residue_pressure_check = {"check": "Default residue pressure values are all 0.0", "status": "PASS"}
    pressure = default_progression.get("residue_pressure", {})
    if not all(v == 0.0 for v in pressure.values()):
        default_residue_pressure_check["status"] = "FAIL"
        default_residue_pressure_check["reason"] = f"Default residue pressure values are not all 0.0: {pressure}"
    audit_results["checks"].append(default_residue_pressure_check)

    # Check 8: Default forbidden flags are all false
    default_forbidden_flags_check = {"check": "Default forbidden flags are all false", "status": "PASS"}
    flags = default_progression.get("forbidden_flags", {})
    if not all(v is False for v in flags.values()):
        default_forbidden_flags_check["status"] = "FAIL"
        default_forbidden_flags_check["reason"] = f"Default forbidden flags are not all false: {flags}"
    audit_results["checks"].append(default_forbidden_flags_check)

    # Create a temporary directory for integration tests
    TEMP_TEST_DIR = os.path.join(project_root, "temp_bootstrapper_tests")
    if os.path.exists(TEMP_TEST_DIR):
        shutil.rmtree(TEMP_TEST_DIR)
    os.makedirs(TEMP_TEST_DIR)
    test_save_path = os.path.join(TEMP_TEST_DIR, "player_save.json")

    # Check 9: Missing save creates valid default when create_if_missing = true
    create_missing_check = {"check": "Missing save creates valid default when create_if_missing = true", "status": "PASS"}
    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=True)
    if not (result["ok"] and os.path.exists(test_save_path) and result["payload"]["level"] == 1):
        create_missing_check["status"] = "FAIL"
        create_missing_check["reason"] = f"Failed to create default save: {result}"
    audit_results["checks"].append(create_missing_check)
    shutil.rmtree(TEMP_TEST_DIR)
    os.makedirs(TEMP_TEST_DIR) # Clean up after this specific test

    # Check 10: Missing save fails safely when create_if_missing = false
    fail_missing_check = {"check": "Missing save fails safely when create_if_missing = false", "status": "PASS"}
    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=False)
    if not (result["ok"] is False and result["error_type"] == "FileNotFound"):
        fail_missing_check["status"] = "FAIL"
        fail_missing_check["reason"] = f"Did not fail safely for missing file when create_if_missing=false: {result}"
    audit_results["checks"].append(fail_missing_check)

    # Check 11: Invalid save fails safely
    invalid_save_fails_check = {"check": "Invalid save fails safely", "status": "PASS"}
    invalid_save_path = os.path.join(TEMP_TEST_DIR, "invalid_player_save.json")
    # Manually write invalid JSON
    with open(invalid_save_path, 'w') as f:
        json.dump({"level": "not_an_int"}, f)
    result = player_progression_bootstrapper.bootstrap_player_progression(invalid_save_path, create_if_missing=True)
    if not (result["ok"] is False and result["error_type"] == "SchemaValidationFailure"):
        invalid_save_fails_check["status"] = "FAIL"
        invalid_save_fails_check["reason"] = f"Invalid save did not fail safely: {result}"
    audit_results["checks"].append(invalid_save_fails_check)
    
    # Check 12: Valid existing save loads successfully
    valid_load_check = {"check": "Valid existing save loads successfully", "status": "PASS"}
    existing_save_path = os.path.join(TEMP_TEST_DIR, "existing_valid_player_save.json")
    # Use json_save_manager to create a valid save
    existing_progression = player_progression_bootstrapper.make_default_player_progression()
    existing_progression["level"] = 5 # Modify to check if loaded correctly
    json_save_manager.save_validated_json(existing_save_path, existing_progression, PLAYER_PROGRESSION_SCHEMA_PATH)
    result = player_progression_bootstrapper.bootstrap_player_progression(existing_save_path, create_if_missing=True)
    if not (result["ok"] and result["payload"]["level"] == 5):
        valid_load_check["status"] = "FAIL"
        valid_load_check["reason"] = f"Failed to load valid existing save: {result}"
    audit_results["checks"].append(valid_load_check)


    # Check 13: Debug=true does not break bootstrap
    debug_not_break_check = {"check": "Debug=true does not break bootstrap", "status": "PASS"}
    debug_test_path = os.path.join(TEMP_TEST_DIR, "debug_bootstrap_save.json")
    try:
        # Assuming debug_logger exists due to import attempts
        with patch('engine.player.bootstrap.player_progression_bootstrapper._debug_logger_available', True):
            with patch('engine.player.bootstrap.player_progression_bootstrapper.debug_logger.write_debug_event') as mock_write_event:
                with patch('engine.player.bootstrap.player_progression_bootstrapper.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True}) as mock_make_event:
                    result = player_progression_bootstrapper.bootstrap_player_progression(debug_test_path, debug=True)
                    if not result["ok"]:
                        debug_not_break_check["status"] = "FAIL"
                        debug_not_break_check["reason"] = f"Bootstrap failed with debug=True: {result}"
                    if not mock_make_event.called or not mock_write_event.called:
                        debug_not_break_check["status"] = "FAIL"
                        debug_not_break_check["reason"] = "Debug logging functions were not called when debug=True."
    except Exception as e:
        debug_not_break_check["status"] = "FAIL"
        debug_not_break_check["reason"] = f"Debug logging unexpectedly broke bootstrap: {e}"
    audit_results["checks"].append(debug_not_break_check)
    

    # Check 14: No database/cloud/network/combat/itemization/skill-tree/rendering/GPU code is introduced
    no_gameplay_code_check = {"check": "No database/cloud/network/combat/itemization/skill-tree/rendering/GPU code is introduced", "status": "PASS"}
    # This is a conceptual check, rely on code review. For automated check, inspect keywords.
    # Open the bootstrapper file and check for forbidden keywords
    with open(bootstrapper_path, 'r', encoding='utf-8') as f:
        content = f.read()
        forbidden_keywords = ["sqlite", "mongo", "http", "socket", "combat_logic", "skill_tree",
                              "itemization", "multiplayer", "render", "gpu_code"]
        for keyword in forbidden_keywords:
            if keyword in content:
                no_gameplay_code_check["status"] = "FAIL"
                no_gameplay_code_check["reason"] = f"Forbidden keyword '{keyword}' found in player_progression_bootstrapper.py."
                break
    audit_results["checks"].append(no_gameplay_code_check)

    # Clean up temporary test directory
    shutil.rmtree(TEMP_TEST_DIR)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_020_player_progression_bootstrap_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_020_player_progression_bootstrap_result.json")

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
    
    # Reload modules to ensure latest changes are picked up
    import importlib
    importlib.reload(player_progression_bootstrapper)
    
    audit = run_player_progression_audit()
    print(json.dumps(audit, indent=2))
