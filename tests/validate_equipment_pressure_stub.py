import os
import json
import subprocess
import sys

def run_equipment_pressure_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-058",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Check Files
    files_to_check = [
        "engine/equipment/runtime/equipment_pressure_stub.py",
        "engine/equipment/runtime/tests/test_equipment_pressure_stub.py",
        "docs/design/equipment/minimal_equipment_pressure_stub.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Check for required functions in equipment_pressure_stub.py
    try:
        from engine.equipment.runtime import equipment_pressure_stub
        required_functions = [
            "calculate_aggregate_equipment_pressure",
            "build_equipment_loadout",
            "validate_equipment_item",
            "validate_equipment_loadout",
            "summarize_equipment_pressure"
        ]
        for func_name in required_functions:
            audit_results["checks"].append({
                "check": f"Function exists: {func_name}",
                "status": "PASS" if hasattr(equipment_pressure_stub, func_name) else "FAIL"
            })
    except Exception as e:
        audit_results["checks"].append({"check": "Import equipment_pressure_stub", "status": "FAIL", "reason": str(e)})

    # 3. Run unit tests
    try:
        test_result = subprocess.run(
            ["py", "-m", "pytest", "engine/equipment/runtime/tests/test_equipment_pressure_stub.py"],
            capture_output=True, text=True
        )
        audit_results["checks"].append({
            "check": "Equipment pressure unit tests pass",
            "status": "PASS" if test_result.returncode == 0 else "FAIL",
            "reason": test_result.stdout if test_result.returncode != 0 else None
        })
    except Exception as e:
        audit_results["checks"].append({"check": "Run unit tests", "status": "FAIL", "reason": str(e)})

    # 4. Verify pressure values and safety logic
    if "equipment_pressure_stub" in sys.modules:
        # Test empty loadout
        empty_agg = equipment_pressure_stub.calculate_aggregate_equipment_pressure([])
        empty_ok = all(v == 0.0 for v in empty_agg.values())
        audit_results["checks"].append({
            "check": "Empty loadout produces zeroed aggregate pressure",
            "status": "PASS" if empty_ok else "FAIL"
        })
        
        # Test dirty item
        dirty_item = {
            "bounded_flags": {"grants_invulnerability": True, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
        }
        dirty_loadout = equipment_pressure_stub.build_equipment_loadout("p1", [dirty_item])
        dirty_ok = dirty_loadout["bounded_rules_clean"] is False
        audit_results["checks"].append({
            "check": "Violation detected if item grants invulnerability",
            "status": "PASS" if dirty_ok else "FAIL"
        })

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"

    # Write audit file
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_058_equipment_pressure_stub_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    # Write result file
    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_058_equipment_pressure_stub_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_equipment_pressure_audit()
    print(json.dumps(audit, indent=2))
