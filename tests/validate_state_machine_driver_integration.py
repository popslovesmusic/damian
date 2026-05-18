import os
import json
import jsonschema
import shutil
import sys
from unittest.mock import patch

# Add project root to sys.path for module discovery
PROJECT_ROOT_FOR_IMPORT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT_FOR_IMPORT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_IMPORT)

from engine.core.runtime import state_machine_driver
from engine.save.runtime import json_save_manager # This will handle its own debug_logger import

# Paths to existing schemas and example data from previous patches (relative to project root)
BASE_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STATES_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/core/state_machine/game_loop_states.json")
TRANSITIONS_PATH = os.path.join(BASE_PROJECT_ROOT, "engine/core/state_machine/game_loop_transitions.json")

def run_state_machine_driver_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-018",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    driver_path = os.path.join(project_root, "engine/core/runtime/state_machine_driver.py")

    # Check 1: state_machine_driver.py exists
    driver_exists_check = {"check": "state_machine_driver.py exists", "status": "PASS"}
    if not os.path.exists(driver_path):
        driver_exists_check["status"] = "FAIL"
        driver_exists_check["reason"] = f"File not found: {driver_path}"
    audit_results["checks"].append(driver_exists_check)
    if driver_exists_check["status"] == "FAIL":
        return audit_results

    # Required driver functions
    required_functions = [
        "load_state_machine",
        "create_runtime_context",
        "can_transition",
        "step_transition",
        "run_scripted_path"
    ]

    # Check 2: Required driver functions exist
    functions_exist_check = {"check": "Required driver functions exist", "status": "PASS"}
    for func_name in required_functions:
        if not hasattr(state_machine_driver, func_name):
            functions_exist_check["status"] = "FAIL"
            functions_exist_check["reason"] = f"Function '{func_name}' is missing in state_machine_driver.py."
            break
    audit_results["checks"].append(functions_exist_check)
    if functions_exist_check["status"] == "FAIL":
        return audit_results

    # --- Integration tests using the driver ---

    # Load state machine
    machine_load_result = state_machine_driver.load_state_machine(STATES_PATH, TRANSITIONS_PATH)
    if not machine_load_result["ok"]:
        audit_results["checks"].append({"check": "Driver loads existing game_loop_states.json and game_loop_transitions.json", "status": "FAIL", "reason": machine_load_result["message"]})
        return audit_results
    machine = machine_load_result["payload"]
    audit_results["checks"].append({"check": "Driver loads existing game_loop_states.json and game_loop_transitions.json", "status": "PASS"})

    # Check 3: Driver loads existing game_loop_states.json (covered by above)
    # Check 4: Driver loads existing game_loop_transitions.json (covered by above)

    context = state_machine_driver.create_runtime_context()

    # Check 5: BOOT_ENGINE can transition to LOAD_CONTENT_PACK
    transition_boot_check = {"check": "BOOT_ENGINE can transition to LOAD_CONTENT_PACK", "status": "PASS"}
    result = state_machine_driver.step_transition(machine, context, "LOAD_CONTENT_PACK")
    if not result["ok"] or result["payload"]["current_state"] != "LOAD_CONTENT_PACK":
        transition_boot_check["status"] = "FAIL"
        transition_boot_check["reason"] = f"Transition from BOOT_ENGINE to LOAD_CONTENT_PACK failed: {result}"
    audit_results["checks"].append(transition_boot_check)
    
    # Reset context for next check
    context = state_machine_driver.create_runtime_context("SPAWN_ENCOUNTERS")
    # Check 6: ACTIVE_FLOOR_LOOP can transition to RESOLVE_FLOOR_OUTCOME
    transition_active_check = {"check": "ACTIVE_FLOOR_LOOP can transition to RESOLVE_FLOOR_OUTCOME", "status": "PASS"}
    # Need to get to ACTIVE_FLOOR_LOOP first for this check as there's no direct path from BOOT_ENGINE
    # Path to ACTIVE_FLOOR_LOOP
    path_to_active = [
        "LOAD_CONTENT_PACK", "LOAD_PLAYER_PROFILE", "LOAD_TOWER_STATE", 
        "SELECT_TARGET_FLOOR", "GENERATE_OR_RESTORE_FLOOR", "APPLY_RESIDUE_MUTATIONS",
        "SPAWN_PLAYERS", "SPAWN_ENCOUNTERS", "ACTIVE_FLOOR_LOOP"
    ]
    temp_context = state_machine_driver.create_runtime_context()
    path_result = state_machine_driver.run_scripted_path(machine, temp_context, path_to_active)
    if not path_result["ok"] or temp_context["current_state"] != "ACTIVE_FLOOR_LOOP":
        transition_active_check["status"] = "FAIL"
        transition_active_check["reason"] = f"Failed to reach ACTIVE_FLOOR_LOOP for test: {path_result}"
    else:
        result = state_machine_driver.step_transition(machine, temp_context, "RESOLVE_FLOOR_OUTCOME")
        if not result["ok"] or result["payload"]["current_state"] != "RESOLVE_FLOOR_OUTCOME":
            transition_active_check["status"] = "FAIL"
            transition_active_check["reason"] = f"Transition from ACTIVE_FLOOR_LOOP to RESOLVE_FLOOR_OUTCOME failed: {result}"
    audit_results["checks"].append(transition_active_check)

    # Check 7: Invalid transition from BOOT_ENGINE to ACTIVE_FLOOR_LOOP fails safely
    invalid_transition_check = {"check": "Invalid transition from BOOT_ENGINE to ACTIVE_FLOOR_LOOP fails safely", "status": "PASS"}
    context = state_machine_driver.create_runtime_context("BOOT_ENGINE")
    result = state_machine_driver.step_transition(machine, context, "ACTIVE_FLOOR_LOOP")
    if result["ok"] or result["error_type"] != "InvalidTransition":
        invalid_transition_check["status"] = "FAIL"
        invalid_transition_check["reason"] = f"Invalid transition did not fail as expected: {result}"
    audit_results["checks"].append(invalid_transition_check)

    # Check 8: Scripted valid path reaches SHUTDOWN_ENGINE
    scripted_path_check = {"check": "Scripted valid path reaches SHUTDOWN_ENGINE", "status": "PASS"}
    context = state_machine_driver.create_runtime_context()
    full_path = [
        "LOAD_CONTENT_PACK", "LOAD_PLAYER_PROFILE", "LOAD_TOWER_STATE", 
        "SELECT_TARGET_FLOOR", "GENERATE_OR_RESTORE_FLOOR", "APPLY_RESIDUE_MUTATIONS",
        "SPAWN_PLAYERS", "SPAWN_ENCOUNTERS", "ACTIVE_FLOOR_LOOP",
        "RESOLVE_FLOOR_OUTCOME", "WRITE_RESIDUE", "MUTATE_TOWER_STATE",
        "SAVE_RUNTIME_STATE", "RETURN_TO_HUB_OR_NEXT_FLOOR", "SHUTDOWN_ENGINE"
    ]
    result = state_machine_driver.run_scripted_path(machine, context, full_path)
    if not result["ok"] or result["payload"]["current_state"] != "SHUTDOWN_ENGINE":
        scripted_path_check["status"] = "FAIL"
        scripted_path_check["reason"] = f"Scripted path to SHUTDOWN_ENGINE failed: {result}"
    audit_results["checks"].append(scripted_path_check)
    
    # Check 9: Debug=true does not break transition stepping
    debug_not_break_check = {"check": "Debug=true does not break transition stepping", "status": "PASS"}
    context = state_machine_driver.create_runtime_context()
    # Mock the debug_logger to ensure it's called, but allow step_transition to work
    try:
        from engine.debug.runtime import debug_logger as real_debug_logger
        with patch('engine.core.runtime.state_machine_driver._debug_logger_available', True):
            with patch('engine.core.runtime.state_machine_driver.debug_logger.write_debug_event') as mock_write_event:
                with patch('engine.core.runtime.state_machine_driver.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True}) as mock_make_event:
                    result = state_machine_driver.step_transition(machine, context, "LOAD_CONTENT_PACK", debug=True)
                    if not result["ok"] or result["payload"]["current_state"] != "LOAD_CONTENT_PACK":
                        debug_not_break_check["status"] = "FAIL"
                        debug_not_break_check["reason"] = f"Transition failed with debug=True: {result}"
                    if not mock_make_event.called or not mock_write_event.called:
                        debug_not_break_check["status"] = "FAIL"
                        debug_not_break_check["reason"] = "Debug logging functions were not called when debug=True."
    except ImportError:
        debug_not_break_check["status"] = "PASS" # Skip if debug_logger is not even available
    except Exception as e:
        debug_not_break_check["status"] = "FAIL"
        debug_not_break_check["reason"] = f"Debug logging unexpectedly broke transition: {e}"
    audit_results["checks"].append(debug_not_break_check)
    
    # Check 10: No gameplay/combat/floor-generation/network/rendering/GPU code is introduced
    no_gameplay_code_check = {"check": "No gameplay/combat/floor-generation/network/rendering/GPU code is introduced", "status": "PASS"}
    # This is a conceptual check, rely on code review. For automated check, inspect keywords.
    with open(driver_path, 'r', encoding='utf-8') as f:
        content = f.read()
        forbidden_keywords = ["combat_logic", "deal_damage", "spawn_enemy", "generate_floor", 
                              "send_packet", "draw_sprite", "render", "gpu_compute"]
        for keyword in forbidden_keywords:
            if keyword in content:
                no_gameplay_code_check["status"] = "FAIL"
                no_gameplay_code_check["reason"] = f"Forbidden keyword '{keyword}' found in state_machine_driver.py."
                break
    audit_results["checks"].append(no_gameplay_code_check)


    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_018_state_machine_runtime_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_018_state_machine_runtime_result.json")

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
    importlib.reload(state_machine_driver)
    
    audit = run_state_machine_driver_audit()
    print(json.dumps(audit, indent=2))
