import os
import json
import jsonschema
import sys

# Add project root to sys.path to import engine
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from engine.room_graph.runtime import room_graph_builder

def run_room_graph_builder_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-042",
        "verdict": "FAIL",
        "checks": []
    }

    # Paths
    builder_path = os.path.join(project_root, "engine/room_graph/runtime/room_graph_builder.py")
    
    # Check 1: room_graph_builder.py exists
    exists_check = {"check": "room_graph_builder.py exists", "status": "PASS"}
    if not os.path.exists(builder_path):
        exists_check["status"] = "FAIL"
        exists_check["reason"] = "File not found"
    audit_results["checks"].append(exists_check)

    if exists_check["status"] == "FAIL":
        write_results(audit_results)
        return audit_results

    # Check 2: Required room graph builder functions exist
    required_funcs = ["make_room_node", "build_room_graph", "validate_room_graph", "summarize_room_graph"]
    funcs_check = {"check": "Required room graph builder functions exist", "status": "PASS"}
    missing_funcs = [func for func in required_funcs if not hasattr(room_graph_builder, func)]
    if missing_funcs:
        funcs_check["status"] = "FAIL"
        funcs_check["reason"] = f"Missing functions: {', '.join(missing_funcs)}"
    audit_results["checks"].append(funcs_check)

    # Setup for functional checks
    floor_record = {"floor_id": 42}
    
    # Check 3: build_room_graph creates schema-compatible graph
    schema_check = {"check": "build_room_graph creates schema-compatible graph", "status": "PASS"}
    result = room_graph_builder.build_room_graph(floor_record)
    if not result["ok"]:
        schema_check["status"] = "FAIL"
        schema_check["reason"] = f"Builder failed: {result.get('message')}"
    else:
        validation = room_graph_builder.validate_room_graph(result["payload"])
        if not validation["ok"]:
            schema_check["status"] = "FAIL"
            schema_check["reason"] = f"Schema validation failed: {validation.get('message')}"
    audit_results["checks"].append(schema_check)

    # Check 4: build_room_graph is deterministic for same floor_record
    deterministic_check = {"check": "build_room_graph is deterministic for same floor_record", "status": "PASS"}
    result2 = room_graph_builder.build_room_graph(floor_record)
    if result["payload"] != result2["payload"]:
        deterministic_check["status"] = "FAIL"
        deterministic_check["reason"] = "Results differ for same input"
    audit_results["checks"].append(deterministic_check)

    # Check 5 & 6: Default graph includes required rooms
    required_rooms_check = {"check": "Default graph includes all required rooms", "status": "PASS"}
    nodes = result["payload"]["nodes"]
    node_types = [n["node_type"] for n in nodes]
    expected_types = ["entry_room", "combat_room", "pressure_room", "recovery_room", "exit_room"]
    missing_types = [t for t in expected_types if t not in node_types]
    if missing_types:
        required_rooms_check["status"] = "FAIL"
        required_rooms_check["reason"] = f"Missing node types: {', '.join(missing_types)}"
    audit_results["checks"].append(required_rooms_check)

    # Check 7: Graph preserves entry_node_id and exit_node_id
    id_preservation_check = {"check": "Graph preserves entry_node_id and exit_node_id", "status": "PASS"}
    if result["payload"]["entry_node_id"] != "entry_a" or result["payload"]["exit_node_id"] != "exit_a":
        id_preservation_check["status"] = "FAIL"
        id_preservation_check["reason"] = f"IDs not preserved: {result['payload']['entry_node_id']}, {result['payload']['exit_node_id']}"
    audit_results["checks"].append(id_preservation_check)

    # Check 8 & 9: Identity and Playability preserved
    preservation_check = {"check": "Identity and Playability preserved", "status": "PASS"}
    if not result["payload"]["identity_preserved"] or not result["payload"]["playability_preserved"]:
        preservation_check["status"] = "FAIL"
        preservation_check["reason"] = "Identity or Playability not preserved"
    audit_results["checks"].append(preservation_check)

    # Check 10 & 11: include_survivor_mark_room support
    survivor_check = {"check": "include_survivor_mark_room support", "status": "PASS"}
    survivor_result = room_graph_builder.build_room_graph(floor_record, include_survivor_mark_room=True)
    s_graph = survivor_result["payload"]
    s_node_types = [n["node_type"] for n in s_graph["nodes"]]
    if "survivor_mark_room" not in s_node_types or not s_graph["survivor_mark_nodes"]:
        survivor_check["status"] = "FAIL"
        survivor_check["reason"] = "Survivor mark room not added or not tracked"
    audit_results["checks"].append(survivor_check)

    # Check 12: Invalid floor_record fails safely
    safe_fail_check = {"check": "Invalid floor_record fails safely", "status": "PASS"}
    fail_result = room_graph_builder.build_room_graph(None)
    if fail_result["ok"]:
        safe_fail_check["status"] = "FAIL"
        safe_fail_check["reason"] = "Builder should have failed on None record"
    audit_results["checks"].append(safe_fail_check)

    # Check 13: Unsupported domain_archetype fails safely
    unsupported_check = {"check": "Unsupported domain_archetype fails safely", "status": "PASS"}
    u_result = room_graph_builder.build_room_graph(floor_record, domain_archetype="unknown")
    if u_result["ok"]:
        unsupported_check["status"] = "FAIL"
        unsupported_check["reason"] = "Builder should have failed on unsupported archetype"
    audit_results["checks"].append(unsupported_check)

    # Check 14: Debug=true does not break room graph builder
    debug_check = {"check": "Debug=true does not break room graph builder", "status": "PASS"}
    try:
        d_result = room_graph_builder.build_room_graph(floor_record, debug=True)
        if not d_result["ok"]:
            debug_check["status"] = "FAIL"
            debug_check["reason"] = "Debug=True caused failure"
    except Exception as e:
        debug_check["status"] = "FAIL"
        debug_check["reason"] = f"Debug=True raised exception: {e}"
    audit_results["checks"].append(debug_check)

    # Check 15: No forbidden code (simple check)
    forbidden_check = {"check": "No forbidden systems introduced", "status": "PASS"}
    with open(builder_path, 'r') as f:
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
    audit_file_path = os.path.join(output_dir, "tower_engine_042_room_graph_builder_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_042_room_graph_builder_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_room_graph_builder_audit()
    print(json.dumps(audit, indent=2))
