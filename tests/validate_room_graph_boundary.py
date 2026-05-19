import os
import json
import jsonschema

def run_room_graph_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-041",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths
    registry_path = os.path.join(project_root, "engine/room_graph/room_graph_registry.json")
    room_schema_path = os.path.join(project_root, "engine/room_graph/contracts/room_node.schema.json")
    graph_schema_path = os.path.join(project_root, "engine/room_graph/contracts/room_graph.schema.json")
    example_graph_path = os.path.join(project_root, "engine/room_graph/contracts/example_room_graph.json")

    # Load files
    def load_json_file(file_path, description):
        try:
            if not os.path.exists(file_path):
                audit_results["checks"].append({"check": f"{description} exists", "status": "FAIL", "reason": "File not found"})
                return None
            with open(file_path, 'r') as f:
                data = json.load(f)
                audit_results["checks"].append({"check": f"{description} exists", "status": "PASS"})
                return data
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "room_graph_registry.json")
    room_schema_data = load_json_file(room_schema_path, "room_node.schema.json")
    graph_schema_data = load_json_file(graph_schema_path, "room_graph.schema.json")
    example_graph_data = load_json_file(example_graph_path, "example_room_graph.json")

    if not all([registry_data, room_schema_data, graph_schema_data, example_graph_data]):
        write_results(project_root, audit_results)
        return audit_results

    # Check 1: Room graph registry includes mutation support rules
    mutation_rules_check = {"check": "Room graph registry includes mutation support rules", "status": "PASS"}
    if not registry_data.get("mutation_support_rules"):
        mutation_rules_check["status"] = "FAIL"
        mutation_rules_check["reason"] = "mutation_support_rules missing or empty"
    audit_results["checks"].append(mutation_rules_check)

    # Check 2: Room graph registry includes survivor mark support
    survivor_support_check = {"check": "Room graph registry includes survivor mark support", "status": "PASS"}
    core_principles = registry_data.get("core_principles", [])
    if "survivor_marks_must_remain_discoverable" not in core_principles:
        survivor_support_check["status"] = "FAIL"
        survivor_support_check["reason"] = "'survivor_marks_must_remain_discoverable' principle missing"
    audit_results["checks"].append(survivor_support_check)

    # Check 3: Example room graph validates against schemas
    example_validation_check = {"check": "Example room graph validates against schemas", "status": "PASS"}
    try:
        # Cross-reference room_node.schema.json
        resolver = jsonschema.RefResolver(
            base_uri=f"file://{os.path.dirname(graph_schema_path).replace('\\', '/')}/",
            referrer=graph_schema_data
        )
        jsonschema.validate(instance=example_graph_data, schema=graph_schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 4: Example graph includes reachable exit
    reachable_exit_check = {"check": "Example graph includes reachable exit", "status": "PASS"}
    entry_id = example_graph_data.get("entry_node_id")
    exit_id = example_graph_data.get("exit_node_id")
    nodes = {node["node_id"]: node for node in example_graph_data.get("nodes", [])}
    
    def can_reach_exit(current_id, visited):
        if current_id == exit_id:
            return True
        if current_id in visited or current_id not in nodes:
            return False
        visited.add(current_id)
        for neighbor in nodes[current_id].get("connections", []):
            if can_reach_exit(neighbor, visited):
                return True
        return False

    if not can_reach_exit(entry_id, set()):
        reachable_exit_check["status"] = "FAIL"
        reachable_exit_check["reason"] = f"Exit {exit_id} not reachable from entry {entry_id}"
    audit_results["checks"].append(reachable_exit_check)

    # Check 5: Example graph includes survivor_mark_room
    survivor_room_check = {"check": "Example graph includes survivor_mark_room", "status": "PASS"}
    has_survivor_room = any(node["node_type"] == "survivor_mark_room" for node in example_graph_data.get("nodes", []))
    if not has_survivor_room:
        survivor_room_check["status"] = "FAIL"
        survivor_room_check["reason"] = "No survivor_mark_room found in example graph"
    audit_results["checks"].append(survivor_room_check)

    # Check 6: Example graph mutation_level >= 1
    mutation_level_check = {"check": "Example graph mutation_level >= 1", "status": "PASS"}
    if example_graph_data.get("mutation_level", 0) < 1:
        mutation_level_check["status"] = "FAIL"
        mutation_level_check["reason"] = "mutation_level is less than 1"
    audit_results["checks"].append(mutation_level_check)

    # Check 7: Example graph identity_preserved = true
    identity_check = {"check": "Example graph identity_preserved = true", "status": "PASS"}
    if example_graph_data.get("identity_preserved") is not True:
        identity_check["status"] = "FAIL"
        identity_check["reason"] = "identity_preserved is not true"
    audit_results["checks"].append(identity_check)

    # Check 8: Example graph playability_preserved = true
    playability_check = {"check": "Example graph playability_preserved = true", "status": "PASS"}
    if example_graph_data.get("playability_preserved") is not True:
        playability_check["status"] = "FAIL"
        playability_check["reason"] = "playability_preserved is not true"
    audit_results["checks"].append(playability_check)

    # Check 9: No room graph runtime implementation is introduced
    runtime_check = {"check": "No room graph runtime implementation is introduced", "status": "PASS"}
    runtime_dir = os.path.join(project_root, "engine/room_graph/runtime")
    if os.path.exists(runtime_dir) and os.listdir(runtime_dir):
        runtime_check["status"] = "FAIL"
        runtime_check["reason"] = "Runtime directory exists and is not empty"
    audit_results["checks"].append(runtime_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    write_results(project_root, audit_results)
    return audit_results

def write_results(project_root, audit_results):
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_041_room_graph_boundary_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_041_room_graph_boundary_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_room_graph_boundary_audit()
    print(json.dumps(audit, indent=2))
