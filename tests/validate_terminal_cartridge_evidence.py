import os
import json
import shutil

def run_terminal_cartridge_evidence_validation():
    audit_results = {
        "patch_id": "STAGE-032-TERMINAL",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    
    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )

    # Check: content status command
    res = term.execute("content status")
    if "Cartridge Verification Status" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports cartridge verification status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports cartridge verification status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "admin_terminal_cartridge_evidence_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Terminal cartridge evidence report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_terminal_cartridge_evidence_validation()
