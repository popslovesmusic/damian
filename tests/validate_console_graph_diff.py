import os
import json
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from engine.console.runtime import mvp_text_console

def run_console_graph_diff_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-044",
        "verdict": "FAIL",
        "checks": []
    }

    # Paths
    console_path = os.path.join(project_root, "engine/console/runtime/mvp_text_console.py")
    test_path = os.path.join(project_root, "engine/console/runtime/tests/test_mvp_text_console_graph_diff.py")
    
    # Check 1: mvp_text_console.py exists and is updated
    exists_check = {"check": "mvp_text_console.py updated", "status": "PASS"}
    if not os.path.exists(console_path):
        exists_check["status"] = "FAIL"
        exists_check["reason"] = "File not found"
    else:
        with open(console_path, 'r') as f:
            content = f.read()
            if "room_graph_mutation_evidence" not in content:
                exists_check["status"] = "FAIL"
                exists_check["reason"] = "room_graph_mutation_evidence integration missing"
    audit_results["checks"].append(exists_check)

    # Check 2: Graph diff console test file exists
    test_exists_check = {"check": "Graph diff console test file exists", "status": "PASS"}
    if not os.path.exists(test_path):
        test_exists_check["status"] = "FAIL"
        test_exists_check["reason"] = "Test file not found"
    audit_results["checks"].append(test_exists_check)

    # Functional Checks using the console runtime
    test_dir = "test_temp_audit_console_graph_diff"
    os.makedirs(test_dir, exist_ok=True)
    paths = {
        "tower_state": os.path.join(test_dir, "tower_state.json"),
        "player_progression": os.path.join(test_dir, "player_progression.json"),
        "system_registry": os.path.join(test_dir, "system_registry.json")
    }
    with open(paths["tower_state"], 'w') as f:
        json.dump({
            "tower_state_id": "audit_tower",
            "engine_version": "0.0.1",
            "content_pack_id": "damian",
            "current_floor": 1,
            "highest_floor_reached": 1,
            "total_runs": 1,
            "total_deaths": 0,
            "floor_memory": [],
            "global_residue": {},
            "last_outcome": "NONE",
            "updated_at": "2026-05-19T00:00:00Z"
        }, f)
    with open(paths["player_progression"], 'w') as f:
        json.dump({
            "player_id": "audit_player",
            "profile_id": "profile_123",
            "content_pack_id": "damian",
            "level": 1,
            "highest_floor_reached": 1,
            "active_orientation": "default",
            "stats": {
                "health": 100.0, "damage": 10.0, "defense": 10.0, "speed": 1.0, "recovery": 1.0
            },
            "unlocked_skills": [],
            "equipped_items": [],
            "residue_pressure": {
                "dominant_build_visibility": 0.0, "power_use_strain": 0.0, "overoptimization_pressure": 0.0
            },
            "forbidden_flags": {
                "permanent_invulnerability": False, "infinite_damage_scaling": False, 
                "residue_immunity": False, "death_consequence_immunity": False
            }
        }, f)

    # Use default paths from orchestrator instead of manual incomplete ones
    paths = mvp_text_console.mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=test_dir)
    
    session_result = mvp_text_console.start_console_session(paths=paths, debug=True)
    if not session_result["ok"]:
        print(f"DEBUG: Session startup failed. Result: {json.dumps(session_result, indent=2)}")
        audit_results["checks"].append({"check": "Console startup", "status": "FAIL", "reason": "Startup failed"})
    else:
        session_state = session_result["session_state"]
        
        # Check 3: diff command still returns floor-memory diff after defeat
        mvp_text_console.execute_console_command(session_state, {"command": "defeat", "args": []})
        diff_result = mvp_text_console.execute_console_command(session_state, {"command": "diff", "args": []})
        
        payload_check = {"check": "diff command includes floor-memory and room-graph evidence", "status": "PASS"}
        payload = diff_result.get("payload")
        if not payload or "before" not in payload or "after" not in payload:
            payload_check["status"] = "FAIL"
            payload_check["reason"] = "Floor memory diff missing from payload"
        elif "room_graph_evidence" not in payload:
            payload_check["status"] = "FAIL"
            payload_check["reason"] = "Room graph evidence missing from payload"
        audit_results["checks"].append(payload_check)

        # Check 4: graph_changed reported
        graph_change_check = {"check": "diff command reports graph_changed", "status": "PASS"}
        if not payload.get("graph_changed"):
            graph_change_check["status"] = "FAIL"
            graph_change_check["reason"] = "graph_changed is not True"
        audit_results["checks"].append(graph_change_check)

        # Check 5: summary non-empty
        summary_check = {"check": "diff readable_summary is non-empty", "status": "PASS"}
        if not payload.get("readable_summary"):
            summary_check["status"] = "FAIL"
            summary_check["reason"] = "readable_summary is empty"
        audit_results["checks"].append(summary_check)

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    write_results(audit_results)
    return audit_results

def write_results(audit_results):
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_044_console_graph_diff_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_044_console_graph_diff_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_console_graph_diff_audit()
    print(json.dumps(audit, indent=2))
