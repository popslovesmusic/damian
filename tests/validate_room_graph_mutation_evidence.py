import os
import json
import sys

# Add project root to sys.path to import engine
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from engine.room_graph.runtime import room_graph_mutation_evidence

def run_room_graph_mutation_evidence_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-043",
        "verdict": "FAIL",
        "checks": []
    }

    # Paths
    evidence_path = os.path.join(project_root, "engine/room_graph/runtime/room_graph_mutation_evidence.py")
    
    # Check 1: room_graph_mutation_evidence.py exists
    exists_check = {"check": "room_graph_mutation_evidence.py exists", "status": "PASS"}
    if not os.path.exists(evidence_path):
        exists_check["status"] = "FAIL"
        exists_check["reason"] = "File not found"
    audit_results["checks"].append(exists_check)

    if exists_check["status"] == "FAIL":
        write_results(audit_results)
        return audit_results

    # Check 2: Required evidence functions exist
    required_funcs = ["make_before_after_room_graphs", "diff_room_graphs", "make_room_graph_mutation_evidence", "summarize_room_graph_mutation_evidence"]
    funcs_check = {"check": "Required evidence functions exist", "status": "PASS"}
    missing_funcs = [func for func in required_funcs if not hasattr(room_graph_mutation_evidence, func)]
    if missing_funcs:
        funcs_check["status"] = "FAIL"
        funcs_check["reason"] = f"Missing functions: {', '.join(missing_funcs)}"
    audit_results["checks"].append(funcs_check)

    # Setup for functional checks
    floor_record = {"floor_id": 1, "domain_archetype": "tower_domain", "layout_seed": "seed_1"}
    fm_before = {"floor_id": 1, "mutation_level": 0, "unclaimed_easter_eggs": []}
    fm_after = {"floor_id": 1, "mutation_level": 2, "unclaimed_easter_eggs": ["mark_1"]}
    
    # Check 3 & 4: Graphs build successfully
    graphs_result = room_graph_mutation_evidence.make_before_after_room_graphs(floor_record, fm_before, fm_after)
    build_check = {"check": "Graphs build successfully", "status": "PASS"}
    if not graphs_result["ok"]:
        build_check["status"] = "FAIL"
        build_check["reason"] = "make_before_after_room_graphs failed"
    audit_results["checks"].append(build_check)

    # Check 5 & 6: ID and Seed preservation
    preservation_check = {"check": "ID and Seed lineage preserved", "status": "PASS"}
    if graphs_result["ok"]:
        before = graphs_result["before_graph"]
        after = graphs_result["after_graph"]
        if before["floor_id"] != 1 or after["floor_id"] != 1:
            preservation_check["status"] = "FAIL"
            preservation_check["reason"] = "floor_id not preserved"
        if before["layout_seed"] != "seed_1" or after["layout_seed"] != "seed_1":
            preservation_check["status"] = "FAIL"
            preservation_check["reason"] = "layout_seed not preserved"
    audit_results["checks"].append(preservation_check)

    # Evidence checks
    evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(floor_record, fm_before, fm_after)
    
    # Check 7 & 8: Graph changed and survivor mark room added
    change_check = {"check": "Graph changed and survivor mark room detected", "status": "PASS"}
    if not evidence["ok"] or not evidence["graph_changed"] or not evidence["survivor_mark_room_added"]:
        change_check["status"] = "FAIL"
        change_check["reason"] = "Evidence failed to detect changes"
    audit_results["checks"].append(change_check)

    # Check 9: mutation_level_delta
    delta_check = {"check": "mutation_level_delta detected", "status": "PASS"}
    if not evidence["ok"] or evidence["mutation_level_delta"] != 2:
        delta_check["status"] = "FAIL"
        delta_check["reason"] = f"Delta incorrect: {evidence.get('mutation_level_delta')}"
    audit_results["checks"].append(delta_check)

    # Check 10 & 11: Identity and Playability preserved
    pres_check = {"check": "Identity and Playability reported preserved", "status": "PASS"}
    if not evidence["ok"] or not evidence["identity_preserved"] or not evidence["playability_preserved"]:
        pres_check["status"] = "FAIL"
        pres_check["reason"] = "Preservation not reported correctly"
    audit_results["checks"].append(pres_check)

    # Check 12: Readable summary non-empty
    summary_check = {"check": "Readable summary is non-empty", "status": "PASS"}
    if not evidence["ok"] or not evidence["readable_summary"]:
        summary_check["status"] = "FAIL"
        summary_check["reason"] = "Summary is empty or missing"
    audit_results["checks"].append(summary_check)

    # Check 13: Debug=true safe
    debug_check = {"check": "Debug=true is safe", "status": "PASS"}
    try:
        room_graph_mutation_evidence.make_room_graph_mutation_evidence(floor_record, fm_before, fm_after, debug=True)
    except Exception as e:
        debug_check["status"] = "FAIL"
        debug_check["reason"] = f"Debug=true crashed: {e}"
    audit_results["checks"].append(debug_check)

    # Check 14: No forbidden code
    forbidden_check = {"check": "No forbidden systems introduced", "status": "PASS"}
    with open(evidence_path, 'r') as f:
        content = f.read()
        forbidden = ["pygame", "opengl", "gpu", "multiplayer", "network", "pathfinding", "tiles"]
        found = [f for f in forbidden if f in content.lower()]
        if found:
            forbidden_check["status"] = "FAIL"
            forbidden_check["reason"] = f"Found potentially forbidden terms: {', '.join(found)}"
    audit_results["checks"].append(forbidden_check)

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
    audit_file_path = os.path.join(output_dir, "tower_engine_043_room_graph_mutation_evidence_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_043_room_graph_mutation_evidence_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_room_graph_mutation_evidence_audit()
    print(json.dumps(audit, indent=2))
