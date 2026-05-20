import json
import os

def run_qemu_boot_validation():
    audit_results = {
        "patch_id": "STAGE-026",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 1. Check Boundary Contract
    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/qemu_boot_boundary.json")
    if os.path.exists(boundary_path):
        audit_results["checks"].append({"check": "QEMU boot boundary defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "QEMU boot boundary defined", "status": "FAIL"})

    # 2. Check QEMU Config
    config_path = os.path.join(project_root, "os/kiosk/qemu_config.json")
    if os.path.exists(config_path):
        audit_results["checks"].append({"check": "QEMU config schema exists", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "QEMU config schema exists", "status": "FAIL"})

    # 3. Check Launch Plan
    plan_path = os.path.join(project_root, "build/live_os/images/qemu_launch_plan.json")
    if os.path.exists(plan_path):
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        audit_results["checks"].append({"check": "QEMU launch plan generated", "status": "PASS"})
        
        # Verify safety in command string
        cmd = plan["command_string"]
        safety_check = {"check": "Launch plan respects safety boundaries", "status": "PASS"}
        
        if "-net none" not in cmd and "-net user" not in cmd:
            safety_check["status"] = "FAIL"
            safety_check["reason"] = "Network isolation not detected in QEMU command."
        
        if "-virtfs" in cmd:
            safety_check["status"] = "FAIL"
            safety_check["reason"] = "Host file system passthrough detected."
            
        audit_results["checks"].append(safety_check)
    else:
        audit_results["checks"].append({"check": "QEMU launch plan generated", "status": "FAIL"})

    # 4. Check Strategy Doc
    strategy_doc = os.path.join(project_root, "docs/design/os/virtualization_boot_strategy.md")
    if os.path.exists(strategy_doc):
        audit_results["checks"].append({"check": "Virtualization boot strategy documented", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Virtualization boot strategy documented", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_qemu_boot_audit.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"QEMU boot audit written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    run_qemu_boot_validation()
