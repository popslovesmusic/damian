import os
import json
import shutil
import subprocess

def run_persistence_runtime_validation():
    audit_results = {
        "patch_id": "STAGE-029",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_data_dir = os.path.join(project_root, "build/runtime_persistence_test")
    
    # 1. Boundary & Contract Definitions
    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/persistent_partition_boundary.json")
    contract_path = os.path.join(project_root, "engine/os_boundary/contracts/persistent_partition_contract.json")
    
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Persistence boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Persistence boundary and contract defined", "status": "FAIL"})

    # 2. Cleanup and setup test data dir
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)

    # 3. Run Launcher with TOWER_DATA_PATH pointing to test dir
    launcher_path = os.path.join(project_root, "engine/os_boundary/kiosk_launcher.py")
    env = os.environ.copy()
    env["TOWER_DATA_PATH"] = test_data_dir
    env["PYTHONPATH"] = project_root # Ensure engine modules are importable
    
    try:
        subprocess.run(
            ["py", launcher_path],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        audit_results["checks"].append({"check": "Launcher executed successfully with persistence", "status": "PASS"})
    except subprocess.CalledProcessError as e:
        audit_results["checks"].append({
            "check": "Launcher executed successfully with persistence",
            "status": "FAIL",
            "reason": f"Launcher failed. Stderr: {e.stderr}"
        })
        return audit_results

    # 4. Verify Persistence Audit Artifact
    audit_path = os.path.join(project_root, "outputs/audits/kiosk_launcher_persistence_audit.json")
    if os.path.exists(audit_path):
        with open(audit_path, 'r') as f:
            evidence = json.load(f)
        
        # Success Criteria Checks
        checks = [
            ("partition_detected", "Partition detection stub passes"),
            ("mount_validated", "Mount validation passes"),
            ("write_probe_success", "Runtime write verification passes")
        ]
        
        for key, description in checks:
            if evidence.get(key) is True:
                audit_results["checks"].append({"check": description, "status": "PASS"})
            else:
                audit_results["checks"].append({"check": description, "status": "FAIL"})

        # Check folders
        required_folders = [
            "saves/", "logs/", "transcripts/", "mods/", 
            "content_packs/", "crash_reports/", "state_snapshots/"
        ]
        folders_ok = True
        for folder in required_folders:
            if folder not in evidence.get("directories_initialized", []):
                folders_ok = False
                break
        
        if folders_ok:
            audit_results["checks"].append({"check": "Folder initialization stub passes", "status": "PASS"})
        else:
            audit_results["checks"].append({"check": "Folder initialization stub passes", "status": "FAIL", "reason": "Missing folders in initialized list."})

    else:
        audit_results["checks"].append({"check": "Persistence audit artifact generated", "status": "FAIL"})

    # 5. Failure Case: Missing Partition
    shutil.rmtree(test_data_dir) # Delete it
    try:
        subprocess.run(
            ["py", launcher_path],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        audit_results["checks"].append({"check": "Missing partition fails safely", "status": "FAIL", "reason": "Launcher should have failed but exited with success."})
    except subprocess.CalledProcessError:
        audit_results["checks"].append({"check": "Missing partition fails safely", "status": "PASS"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "persistent_partition_runtime_report.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Persistence runtime report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_persistence_runtime_validation()
