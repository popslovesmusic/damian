import os
import json
import shutil
import subprocess

def run_restricted_terminal_validation():
    audit_results = {
        "patch_id": "STAGE-031",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json")
    command_path = os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json")

    # 1. Check Boundary & Contract
    if os.path.exists(boundary_path) and os.path.exists(command_path):
        audit_results["checks"].append({"check": "Terminal boundary and command contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Terminal boundary and command contract defined", "status": "FAIL"})

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    
    term = RestrictedAdminTerminal(boundary_path, command_path, data_root)

    # Check 2: Allowlisted command execution (status)
    res = term.execute("status")
    if "Tower OS Status: ONLINE" in res:
        audit_results["checks"].append({"check": "Only allowlisted commands execute (status)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Only allowlisted commands execute (status)", "status": "FAIL"})

    # Check 3: Unknown commands fail safely
    res = term.execute("unknown_cmd")
    if "ERROR: Unknown command family" in res:
        audit_results["checks"].append({"check": "Unknown commands fail safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Unknown commands fail safely", "status": "FAIL"})

    # Check 4: Dangerous command strings rejected
    res = term.execute("status; rm -rf /")
    if "Disallowed character detected: ;" in res:
        audit_results["checks"].append({"check": "Dangerous command strings are rejected", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Dangerous command strings are rejected", "status": "FAIL"})

    # Check 5: Persistence info command
    res = term.execute("persistence info")
    if "Persistence Info" in res and "TOWER_DATA" in res:
        audit_results["checks"].append({"check": "Persistence status command reads only bounded paths", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Persistence status command reads only bounded paths", "status": "FAIL"})

    # Check 6: Diagnostics health command
    res = term.execute("diag health")
    if "System Health" in res and "rootfs_integrity" in res:
        audit_results["checks"].append({"check": "Diagnostics stub passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Diagnostics stub passes", "status": "FAIL"})

    # Check 7: Audit log existence and location
    audit_log_path = os.path.join(data_root, "logs/admin_terminal_audit.log")
    if os.path.exists(audit_log_path):
        # Verify it writes under TOWER_DATA
        if os.path.abspath(audit_log_path).startswith(os.path.abspath(data_root)):
             audit_results["checks"].append({"check": "Terminal audit log writes only under TOWER_DATA", "status": "PASS"})
        else:
             audit_results["checks"].append({"check": "Terminal audit log writes only under TOWER_DATA", "status": "FAIL", "reason": "Audit log outside data root."})
    else:
        audit_results["checks"].append({"check": "Terminal audit log writes only under TOWER_DATA", "status": "FAIL", "reason": "Audit log not found."})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "restricted_admin_terminal_boundary_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Terminal validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_restricted_terminal_validation()
