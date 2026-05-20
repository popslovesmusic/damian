import os
import json
import jsonschema

def run_room_traversal_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-092",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 1. Check Files
    files_to_check = [
        "engine/room_graph/traversal/room_traversal_boundary.json",
        "engine/room_graph/traversal/contracts/room_traversal_route.schema.json",
        "engine/room_graph/traversal/contracts/example_room_traversal_route.json",
        "docs/design/room_traversal/mvp_room_traversal_graph_boundary.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Validate Boundary Content
    boundary_path = os.path.join(project_root, "engine/room_graph/traversal/room_traversal_boundary.json")
    if os.path.exists(boundary_path):
        with open(boundary_path, 'r') as f:
            boundary = json.load(f)
            
            responsibilities = boundary.get("runtime_responsibilities", [])
            req_resp = ["represent_room_to_room_routes", "preserve_floor_identity"]
            resp_check = all(r in responsibilities for r in req_resp)
            audit_results["checks"].append({"check": "Boundary includes required responsibilities", "status": "PASS" if resp_check else "FAIL"})
            
            policy = boundary.get("route_pressure_policy", {})
            pol_check = (policy.get("routes_should_have_distinct_exposure_profiles") is True and 
                         policy.get("mutation_scars_should_influence_route_pressure") is True and
                         policy.get("critical_route_must_remain_valid") is True)
            audit_results["checks"].append({"check": "Boundary includes required route policies", "status": "PASS" if pol_check else "FAIL"})
            
            identity = boundary.get("identity_rules", [])
            id_check = "room_routes_must_not_bypass_residue" in identity
            audit_results["checks"].append({"check": "Boundary includes residue identity rule", "status": "PASS" if id_check else "FAIL"})

    # 3. Schema Validation of Example
    schema_path = os.path.join(project_root, "engine/room_graph/traversal/contracts/room_traversal_route.schema.json")
    example_path = os.path.join(project_root, "engine/room_graph/traversal/contracts/example_room_traversal_route.json")

    if os.path.exists(schema_path) and os.path.exists(example_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            with open(example_path, 'r') as f:
                example = json.load(f)

            jsonschema.validate(instance=example, schema=schema)
            audit_results["checks"].append({"check": "Example route validates against schema", "status": "PASS"})
            
            # Additional logic checks on example
            exposure = example.get("route_exposure")
            modifier = example.get("escape_modifier")
            
            exposure_ok = (0.0 <= exposure <= 1.0)
            modifier_ok = (-1.0 <= modifier <= 1.0)
            
            audit_results["checks"].append({"check": "Example exposure is in bounds", "status": "PASS" if exposure_ok else "FAIL"})
            audit_results["checks"].append({"check": "Example escape modifier is in bounds", "status": "PASS" if modifier_ok else "FAIL"})
            
            flags_check = (example.get("playability_preserved") is True and 
                           example.get("identity_preserved") is True and 
                           example.get("bounded_flags_clean") is True)
            audit_results["checks"].append({"check": "Example safety flags are True", "status": "PASS" if flags_check else "FAIL"})

        except Exception as e:
            audit_results["checks"].append({"check": "Schema validation", "status": "FAIL", "reason": str(e)})

    # Final Verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"

    # Write Results
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_092_room_traversal_boundary_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_092_room_traversal_boundary_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_room_traversal_boundary_audit()
    print(json.dumps(audit, indent=2))
