import os
import json
import shutil
import subprocess

def run_kiosk_launcher_validation():
    audit_results = {
        "patch_id": "STAGE-023",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_data_dir = os.path.join(project_root, "build/test_tower_data")
    
    # Cleanup and setup test data dir
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)

    audit_results["checks"].append({"check": "Test data directory initialized", "status": "PASS"})

    # Run launcher
    launcher_path = os.path.join(project_root, "engine/os_boundary/kiosk_launcher.py")
    env = os.environ.copy()
    env["TOWER_DATA_PATH"] = test_data_dir
    
    try:
        result = subprocess.run(
            ["py", launcher_path],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        audit_results["checks"].append({"check": "Launcher executed successfully", "status": "PASS"})
    except subprocess.CalledProcessError as e:
        audit_results["checks"].append({
            "check": "Launcher executed successfully",
            "status": "FAIL",
            "reason": f"Launcher failed with exit code {e.returncode}. Stderr: {e.stderr}"
        })
        return audit_results

    # Check 1: Verify folders were created
    folders_created = True
    for folder in ["saves", "logs", "transcripts"]:
        if not os.path.exists(os.path.join(test_data_dir, folder)):
            folders_created = False
            audit_results["checks"].append({"check": f"Folder {folder} created", "status": "FAIL"})
    if folders_created:
        audit_results["checks"].append({"check": "All required folders created in TOWER_DATA", "status": "PASS"})

    # Check 2: Verify handoff report exists
    handoff_report_path = os.path.join(test_data_dir, "logs/launcher_handoff.json")
    if os.path.exists(handoff_report_path):
        with open(handoff_report_path, 'r') as f:
            report = json.load(f)
            if report.get("status") == "READY":
                audit_results["checks"].append({"check": "Handoff report status is READY", "status": "PASS"})
            else:
                audit_results["checks"].append({"check": "Handoff report status is READY", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Handoff report exists", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "stage_023_kiosk_launcher_audit.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    run_kiosk_launcher_validation()
