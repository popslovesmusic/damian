import os
import json
import jsonschema

def run_traversal_runtime_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-085",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 1. Check Files
    files_to_check = [
        "engine/traversal/runtime/traversal_runtime_boundary.json",
        "engine/traversal/runtime/contracts/traversal_event.schema.json",
        "engine/traversal/runtime/contracts/example_traversal_event.json",
        "docs/design/traversal/mvp_traversal_runtime_boundary.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Validate Boundary Content
    boundary_path = os.path.join(project_root, "engine/traversal/runtime/traversal_runtime_boundary.json")
    if os.path.exists(boundary_path):
        with open(boundary_path, 'r') as f:
            boundary = json.load(f)
            
            responsibilities = boundary.get("runtime_responsibilities", [])
            req_resp = ["track_traversal_pressure", "track_escape_pressure"]
            resp_check = all(r in responsibilities for r in req_resp)
            audit_results["checks"].append({"check": "Boundary includes required responsibilities", "status": "PASS" if resp_check else "FAIL"})
            
            policy = boundary.get("traversal_policy", {})
            pol_check = (policy.get("traversal_pressure_should_scale_with_capacity_pressure") is True and 
                         policy.get("traversal_runtime_should_be_deterministic_for_mvp") is True)
            audit_results["checks"].append({"check": "Boundary includes required traversal policy", "status": "PASS" if pol_check else "FAIL"})
            
            identity = boundary.get("identity_rules", [])
            id_check = "traversal_must_not_bypass_residue" in identity
            audit_results["checks"].append({"check": "Boundary includes residue identity rule", "status": "PASS" if id_check else "FAIL"})

    # 3. Schema Validation of Example
    schema_path = os.path.join(project_root, "engine/traversal/runtime/contracts/traversal_event.schema.json")
    example_path = os.path.join(project_root, "engine/traversal/runtime/contracts/example_traversal_event.json")

    if os.path.exists(schema_path) and os.path.exists(example_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            with open(example_path, 'r') as f:
                example = json.load(f)

            jsonschema.validate(instance=example, schema=schema)
            audit_results["checks"].append({"check": "Example event validates against schema", "status": "PASS"})
            
            # Additional logic checks on example
            risk = example.get("escape_risk")
            exposure = example.get("route_exposure")
            
            bounds_ok = (0.0 <= risk <= 1.0) and (0.0 <= exposure <= 1.0)
            audit_results["checks"].append({"check": "Example risk and exposure are in bounds", "status": "PASS" if bounds_ok else "FAIL"})
            
            clean_check = example.get("bounded_flags_clean") is True
            audit_results["checks"].append({"check": "Example bounded_flags_clean is True", "status": "PASS" if clean_check else "FAIL"})

        except Exception as e:
            audit_results["checks"].append({"check": "Schema validation", "status": "FAIL", "reason": str(e)})

    # Final Verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"

    # Write Results
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_085_traversal_runtime_boundary_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_085_traversal_runtime_boundary_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_traversal_runtime_boundary_audit()
    print(json.dumps(audit, indent=2))
