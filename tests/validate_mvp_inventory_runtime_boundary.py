import os
import json
import jsonschema

def run_inventory_runtime_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-062",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 1. Check Files
    files_to_check = [
        "engine/inventory/runtime/inventory_runtime_boundary.json",
        "engine/inventory/runtime/contracts/inventory_transaction.schema.json",
        "engine/inventory/runtime/contracts/example_inventory_transaction.json",
        "docs/design/inventory_runtime/mvp_inventory_runtime_boundary.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Validate Boundary Content
    boundary_path = os.path.join(project_root, "engine/inventory/runtime/inventory_runtime_boundary.json")
    if os.path.exists(boundary_path):
        with open(boundary_path, 'r') as f:
            boundary = json.load(f)
            
            responsibilities = boundary.get("runtime_responsibilities", [])
            req_resp = ["track_item_quantities", "deduct_consumables", "deduct_repair_materials"]
            resp_check = all(r in responsibilities for r in req_resp)
            audit_results["checks"].append({"check": "Boundary includes required responsibilities", "status": "PASS" if resp_check else "FAIL"})
            
            policy = boundary.get("capacity_policy", {})
            cap_check = (policy.get("capacity_pressure_should_accumulate") is True and 
                         policy.get("capacity_pressure_should_not_average") is True)
            audit_results["checks"].append({"check": "Boundary includes required capacity policy", "status": "PASS" if cap_check else "FAIL"})
            
            identity = boundary.get("identity_rules", [])
            id_check = "inventory_must_not_bypass_residue" in identity
            audit_results["checks"].append({"check": "Boundary includes residue identity rule", "status": "PASS" if id_check else "FAIL"})

    # 3. Schema Validation of Example
    schema_path = os.path.join(project_root, "engine/inventory/runtime/contracts/inventory_transaction.schema.json")
    example_path = os.path.join(project_root, "engine/inventory/runtime/contracts/example_inventory_transaction.json")

    if os.path.exists(schema_path) and os.path.exists(example_path):
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            with open(example_path, 'r') as f:
                example = json.load(f)

            jsonschema.validate(instance=example, schema=schema)
            audit_results["checks"].append({"check": "Example transaction validates against schema", "status": "PASS"})
            
            applied_check = example.get("transaction_applied") is True
            audit_results["checks"].append({"check": "Example transaction_applied is True", "status": "PASS" if applied_check else "FAIL"})
            
            cap_valid = example.get("capacity_after") <= example.get("inventory_capacity")
            audit_results["checks"].append({"check": "Example capacity remains within bounds", "status": "PASS" if cap_valid else "FAIL"})
            
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
    audit_file_path = os.path.join(output_dir, "tower_engine_062_inventory_runtime_boundary_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_062_inventory_runtime_boundary_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_inventory_runtime_boundary_audit()
    print(json.dumps(audit, indent=2))
