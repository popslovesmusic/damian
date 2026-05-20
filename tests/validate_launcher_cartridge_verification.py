import os
import json
import shutil
import subprocess

def run_launcher_cartridge_audit():
    audit_results = {
        "patch_id": "STAGE-032-LAUNCHER",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    test_data_dir = os.path.join(project_root, "build/launcher_cartridge_test")
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
    os.makedirs(test_data_dir)

    launcher_path = os.path.join(project_root, "engine/os_boundary/kiosk_launcher.py")
    env = os.environ.copy()
    env["TOWER_DATA_PATH"] = test_data_dir
    env["TOWER_OS_ROOT"] = project_root
    env["PYTHONPATH"] = project_root
    
    try:
        subprocess.run(
            ["py", launcher_path],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        audit_results["checks"].append({"check": "Launcher executed successfully with cartridge verification", "status": "PASS"})
    except subprocess.CalledProcessError as e:
        audit_results["checks"].append({
            "check": "Launcher executed successfully with cartridge verification",
            "status": "FAIL",
            "reason": f"Launcher failed. Stderr: {e.stderr}"
        })
        return audit_results

    # Verify Cartridge Evidence in Audit
    audit_path = os.path.join(project_root, "outputs/audits/kiosk_launcher_cartridge_verification_result.json")
    if os.path.exists(audit_path):
        with open(audit_path, 'r') as f:
            evidence = json.load(f)
        
        if evidence.get("verdict") == "PASS":
             audit_results["checks"].append({"check": "Launcher audit confirms cartridge PASS", "status": "PASS"})
        else:
             audit_results["checks"].append({"check": "Launcher audit confirms cartridge PASS", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Launcher cartridge audit artifact generated", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "kiosk_launcher_cartridge_verification_result_final.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Launcher cartridge audit report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_launcher_cartridge_audit()
