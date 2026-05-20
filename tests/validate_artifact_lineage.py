import os
import json
import shutil
import subprocess

def run_artifact_lineage_validation():
    audit_results = {
        "patch_id": "STAGE-033",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/lineage_test_data")
    if os.path.exists(data_root):
        shutil.rmtree(data_root)
    os.makedirs(data_root)

    # 1. Contract checks
    contracts = [
        "engine/os_boundary/contracts/artifact_lineage_boundary.json",
        "engine/os_boundary/contracts/lineage_manifest_contract.json",
        "engine/os_boundary/contracts/persistent_data_version_contract.json"
    ]
    all_contracts_exist = True
    for c in contracts:
        if not os.path.exists(os.path.join(project_root, c)):
            all_contracts_exist = False
            break
    
    if all_contracts_exist:
        audit_results["checks"].append({"check": "Lineage boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Lineage boundary and contracts defined", "status": "FAIL"})

    # 2. Version Scanner Compatibility (Compatible case)
    version_file = os.path.join(data_root, ".tower_data_version")
    with open(version_file, 'w') as f:
        f.write("1.0.0")
    
    from engine.os_boundary.lineage_manager import LineageManager
    with open(os.path.join(project_root, contracts[0]), 'r') as f:
        boundary_c = json.load(f)
    with open(os.path.join(project_root, contracts[1]), 'r') as f:
        lineage_c = json.load(f)
    with open(os.path.join(project_root, contracts[2]), 'r') as f:
        version_c = json.load(f)

    lm = LineageManager(data_root, boundary_c, lineage_c)
    lm.scan_data_version(version_c)
    evidence = lm.get_final_evidence()
    
    if evidence.get("compatibility") == "COMPATIBLE":
        audit_results["checks"].append({"check": "Version scanner detects compatible data", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Version scanner detects compatible data", "status": "FAIL"})

    # 3. Version Scanner Incompatibility (Incompatible case)
    with open(version_file, 'w') as f:
        f.write("9.9.9")
    lm2 = LineageManager(data_root, boundary_c, lineage_c)
    lm2.scan_data_version(version_c)
    evidence2 = lm2.get_final_evidence()
    if evidence2.get("compatibility") == "INCOMPATIBLE":
        audit_results["checks"].append({"check": "Version scanner detects incompatible data", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Version scanner detects incompatible data", "status": "FAIL"})

    # 4. Migration Dry-Run
    from engine.os_boundary.migration_planner import MigrationPlanner
    mp = MigrationPlanner(data_root, os.path.join(project_root, "build/backups"))
    plan = mp.create_dry_run_plan("1.0.0", "1.1.0")
    if plan["verdict"] == "DRY_RUN_SUCCESS" and len(plan["plan_steps"]) > 0:
        audit_results["checks"].append({"check": "Migration dry-run produces audit", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Migration dry-run produces audit", "status": "FAIL"})

    # 5. Launcher Audit Integration
    launcher_path = os.path.join(project_root, "engine/os_boundary/kiosk_launcher.py")
    env = os.environ.copy()
    # Use compatible version for launcher test
    with open(version_file, 'w') as f:
        f.write("1.0.0")
    env["TOWER_DATA_PATH"] = data_root
    env["TOWER_OS_ROOT"] = project_root
    env["PYTHONPATH"] = project_root
    
    try:
        subprocess.run(["py", launcher_path], env=env, capture_output=True, text=True, check=True)
        audit_path = os.path.join(project_root, "outputs/audits/kiosk_launcher_lineage_result.json")
        if os.path.exists(audit_path):
             audit_results["checks"].append({"check": "Launcher audit reports artifact lineage", "status": "PASS"})
        else:
             audit_results["checks"].append({"check": "Launcher audit reports artifact lineage", "status": "FAIL"})
    except subprocess.CalledProcessError as e:
        audit_results["checks"].append({"check": "Launcher execution", "status": "FAIL", "reason": e.stderr})

    # 6. Admin Terminal Integration
    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, contracts[0].replace("artifact_lineage_boundary", "restricted_terminal_boundary")),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("lineage status")
    if "Artifact Lineage Status" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports lineage status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports lineage status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "artifact_lineage_boundary_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Lineage validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_artifact_lineage_validation()
