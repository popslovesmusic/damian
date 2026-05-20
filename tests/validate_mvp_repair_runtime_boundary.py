import os
import json
import jsonschema

def run_repair_runtime_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-080",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 1. Check Files
    files_to_check = [
        "engine/equipment/repair/repair_runtime_boundary.json",
        "engine/equipment/repair/contracts/repair_event.schema.json",
        "engine/equipment/repair/contracts/example_repair_event.json",
        "docs/design/repair/mvp_repair_runtime_boundary.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Validate Boundary Content
    boundary_path = os.path.join(project_root, "engine/equipment/repair/repair_runtime_boundary.json")
    if os.path.exists(boundary_path):
        with open(boundary_path, 'r') as f:
            boundary = json.load(f)
            
            responsibilities = boundary.get("runtime_responsibilities", [])
            req_resp = ["consume_repair_materials", "restore_bounded_durability", "prevent_over_repair"]
            resp_check = all(r in responsibilities for r in req_resp)
            audit_results["checks"].append({"check": "Boundary includes required responsibilities", "status": "PASS" if resp_check else "FAIL"})
            
            policy = boundary.get("repair_policy", {})
            pol_check = (policy.get("repair_requires_materials") is True and 
                         policy.get("repair_cannot_exceed_maximum_durability") is True)
            audit_results["checks"].append({"check": "Boundary includes required repair policy", "status": "PASS" if pol_check else "FAIL"})
            
            identity = boundary.get("identity_rules", [])
            id_check = "repair_must_not_cancel_residue" in identity
            audit_results["checks"].append({"check": "Boundary includes residue identity rule", "status": "PASS" if id_check else "FAIL"})

    # 3. Schema Validation of Example
    schema_path = os.path.join(project_root, "engine/equipment/repair/contracts/repair_event.schema.json")
    example_path = os.path.join(project_root, "engine/equipment/repair/contracts/example_repair_event.json")

    if os.path.exists(schema_path) and os.path.exists(example_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            with open(example_path, 'r') as f:
                example = json.load(f)

            jsonschema.validate(instance=example, schema=schema)
            audit_results["checks"].append({"check": "Example event validates against schema", "status": "PASS"})
            
            # Logic checks on example
            before = example.get("durability_before")
            after = example.get("durability_after")
            max_d = example.get("maximum_durability")
            restored = example.get("durability_restored")
            
            bounds_ok = (after <= max_d)
            audit_results["checks"].append({"check": "Example durability remains within max bounds", "status": "PASS" if bounds_ok else "FAIL"})
            
            delta_ok = (restored == (after - before))
            audit_results["checks"].append({"check": "Example durability delta is consistent", "status": "PASS" if delta_ok else "FAIL"})
            
            applied_check = example.get("repair_applied") is True
            audit_results["checks"].append({"check": "Example repair_applied is True", "status": "PASS" if applied_check else "FAIL"})
            
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
    audit_file_path = os.path.join(output_dir, "tower_engine_080_repair_runtime_boundary_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_080_repair_runtime_boundary_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_repair_runtime_boundary_audit()
    print(json.dumps(audit, indent=2))
