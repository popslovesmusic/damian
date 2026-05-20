import os
import json
import shutil
import subprocess

def run_recovery_runtime_validation():
    audit_results = {
        "patch_id": "STAGE-037",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/recovery_runtime_boundary.json")
    repair_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/recovery_repair_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(repair_contract_path):
        audit_results["checks"].append({"check": "Recovery boundary and repair contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Recovery boundary and repair contract defined", "status": "FAIL"})

    from engine.os_boundary.recovery_manager import RecoveryManager
    rm = RecoveryManager(data_root, boundary_path, repair_contract_path)

    # 2. Integrity Scanner (Healthy State)
    # Ensure some directories exist and contain items to be HEALTHY
    saves_dir = os.path.join(data_root, "saves/")
    os.makedirs(saves_dir, exist_ok=True)
    with open(os.path.join(saves_dir, "dummy_save.json"), 'w') as f: f.write("{}")
    
    report = rm.scan_integrity()
    if report.get("saves/") == "HEALTHY":
        audit_results["checks"].append({"check": "Integrity scanner detects healthy state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Integrity scanner detects healthy state", "status": "FAIL", "reason": f"Expected HEALTHY, got {report.get('saves/')}"})

    # 3. Integrity Scanner (Corrupted/Missing State)
    shutil.rmtree(os.path.join(data_root, "saves/"))
    report2 = rm.scan_integrity()
    if report2.get("saves/") == "MISSING":
        audit_results["checks"].append({"check": "Integrity scanner detects corrupted state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Integrity scanner detects corrupted state", "status": "FAIL"})

    # 4. Runtime Isolation
    os.makedirs(os.path.join(data_root, "mods/"), exist_ok=True)
    if rm.isolate_corruption("mods/"):
        audit_results["checks"].append({"check": "Corrupted runtime state isolated safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Corrupted runtime state isolated safely", "status": "FAIL"})

    # 5. Recovery Simulation
    if rm.simulate_recovery("SNAP_PROTO_001"):
        audit_results["checks"].append({"check": "Snapshot recovery simulation runs without overwrite", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Snapshot recovery simulation runs without overwrite", "status": "FAIL"})

    # 6. Recovery Audit
    audit_path = os.path.join(project_root, "outputs/audits/recovery_lineage_audit_result.json")
    rm.emit_audit(audit_path)
    if os.path.exists(audit_path):
        with open(audit_path, 'r') as f:
            audit = json.load(f)
        if len(audit.get("actions_taken", [])) > 0:
             audit_results["checks"].append({"check": "Recovery audit preserves lineage metadata", "status": "PASS"})
        else:
             audit_results["checks"].append({"check": "Recovery audit preserves lineage metadata", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Recovery audit preserves lineage metadata", "status": "FAIL", "reason": "Audit file missing."})

    # 7. Admin Terminal Integration
    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("recovery audit")
    if "Recovery Audit Log" in res and "actions_taken" in res:
        audit_results["checks"].append({"check": "Admin terminal exposes bounded recovery commands", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal exposes bounded recovery commands", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "recovery_runtime_validation_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Recovery validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_recovery_runtime_validation()
