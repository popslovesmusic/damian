import os
import json
import shutil
import subprocess

def run_launcher_hardening_validation():
    audit_results = {
        "patch_id": "STAGE-030",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os_root = os.path.join(project_root, "build/live_os/rootfs_staging")
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    
    # 1. Ensure prerequisites exist
    os.makedirs(os_root, exist_ok=True)
    os.makedirs(data_root, exist_ok=True)

    from engine.os_boundary.launcher_hardener import KioskLauncherHardener
    
    hardener = KioskLauncherHardener(os_root, data_root)

    # Check 1: Environment Verification
    if hardener.verify_environment():
        audit_results["checks"].append({"check": "Environment verification passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Environment verification passes", "status": "FAIL"})

    # Check 2: Persistence Path Guard (Valid paths)
    if hardener.enforce_persistence_guard(["saves", "logs", "artifacts"]):
        audit_results["checks"].append({"check": "Persistence path guard accepts valid paths", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Persistence path guard accepts valid paths", "status": "FAIL"})

    # Check 3: Persistence Path Guard (Invalid paths / Escape attempt)
    if not hardener.enforce_persistence_guard(["../outside"]):
        audit_results["checks"].append({"check": "Persistence path guard blocks invalid paths", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Persistence path guard blocks invalid paths", "status": "FAIL"})

    # Check 4: Runtime Config Handoff
    config = hardener.generate_runtime_config()
    required_keys = ["engine_mode", "content_pack_root", "save_root", "log_root", "artifact_root"]
    if all(k in config for k in required_keys):
        audit_results["checks"].append({"check": "Runtime config handoff passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Runtime config handoff passes", "status": "FAIL"})

    # Check 5: Failure Mode Audit
    failure_audit_path = os.path.join(project_root, "outputs/audits/kiosk_launcher_failure_audit.json")
    hardener.emit_failure_audit(failure_audit_path)
    if os.path.exists(failure_audit_path):
        with open(failure_audit_path, 'r') as f:
            fail_report = json.load(f)
            if fail_report.get("verdict") == "FAIL":
                audit_results["checks"].append({"check": "Failure mode audit passes", "status": "PASS"})
            else:
                audit_results["checks"].append({"check": "Failure mode audit passes", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Failure mode audit passes", "status": "FAIL", "reason": "Audit file not created."})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "kiosk_launcher_runtime_contract_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Hardening validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_launcher_hardening_validation()
