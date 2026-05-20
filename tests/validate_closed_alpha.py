import os
import json
import shutil
import subprocess

def run_closed_alpha_validation():
    audit_results = {
        "patch_id": "STAGE-051",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/closed_alpha_boundary.json")
    contract_path = os.path.join(project_root, "engine/os_boundary/contracts/alpha_cohort_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Closed alpha boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Closed alpha boundary and contract defined", "status": "FAIL"})

    from engine.os_boundary.closed_alpha_manager import ClosedAlphaManager
    cam = ClosedAlphaManager(boundary_path, contract_path)

    # 2. Alpha Cohort Generation
    participants = [f"alpha_tester_{i}" for i in range(1, 11)]
    cohort = cam.generate_cohort("wave_001", participants, "1.0.0-rc1")
    if "cohort_hash" in cohort and len(cohort["participant_ids"]) == 10:
        audit_results["checks"].append({"check": "Alpha cohort generation stub produces bounded cohort", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Alpha cohort generation stub produces bounded cohort", "status": "FAIL"})

    # Check max participants limit
    large_cohort = cam.generate_cohort("wave_002", [f"t_{i}" for i in range(100)], "1.0.0-rc1")
    if large_cohort.get("status") == "FAIL":
         audit_results["checks"].append({"check": "Cohort size limit enforced", "status": "PASS"})
    else:
         audit_results["checks"].append({"check": "Cohort size limit enforced", "status": "FAIL"})

    # 3. Offline Telemetry Export
    telemetry = cam.generate_telemetry_export(data_root)
    if "export_id" in telemetry and telemetry["bounded_flags"].get("offline_export") is True:
        audit_results["checks"].append({"check": "Offline telemetry export boundary validates", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Offline telemetry export boundary validates", "status": "FAIL"})

    # 4. Structured Feedback Validation
    valid_feedback = {"participant_id": "tester_1", "category": "UI", "severity": "LOW", "description": "Bug"}
    if cam.validate_structured_feedback(valid_feedback):
        audit_results["checks"].append({"check": "Alpha feedback validation enforces bounded structure", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Alpha feedback validation enforces bounded structure", "status": "FAIL"})

    invalid_feedback = {"participant_id": "tester_1", "description": "Missing category"}
    if not cam.validate_structured_feedback(invalid_feedback):
        audit_results["checks"].append({"check": "Invalid feedback rejected safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Invalid feedback rejected safely", "status": "FAIL"})

    # 5. Admin Terminal Integration
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "alpha_cohort_result.json"), 'w') as f:
        json.dump(cohort, f, indent=2)
    with open(os.path.join(output_dir, "offline_telemetry_export_result.json"), 'w') as f:
        json.dump(telemetry, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("alpha status")
    if "Closed Alpha Cohort Status" in res and "cohort_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports alpha state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports alpha state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_051_closed_alpha_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Closed Alpha validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_closed_alpha_validation()
