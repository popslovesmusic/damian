import os
import json
import shutil
import subprocess

def run_onboarding_validation():
    audit_results = {
        "patch_id": "STAGE-061",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/player/contracts/first_hour_boundary.json")
    contract_path = os.path.join(project_root, "engine/player/contracts/onboarding_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "First-hour boundary and onboarding contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "First-hour boundary and onboarding contract defined", "status": "FAIL"})

    from engine.player.runtime.onboarding_manager import OnboardingManager
    om = OnboardingManager(boundary_path, contract_path)

    # 2. Onboarding Profile Generation
    profile = om.generate_onboarding_profile("survivor_test")
    if "onboarding_hash" in profile and profile["entry_sequence_profile"]["status"] == "INITIALIZED":
        audit_results["checks"].append({"check": "Survivor entry sequence communications tower identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Survivor entry sequence communications tower identity", "status": "FAIL"})

    # 3. Guided Pressure Learning
    advanced = om.advance_onboarding(profile, "FIRST_COMBAT")
    if advanced["combat_teaching_profile"]["state"] == "ACTIVE_FEEDBACK":
        audit_results["checks"].append({"check": "Guided pressure learning remains contextual", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Guided pressure learning remains contextual", "status": "FAIL"})

    # 4. Failure Teaching
    failed = om.advance_onboarding(advanced, "FIRST_FAILURE")
    if failed["failure_teaching_profile"]["first_failure_demonstrated"] is True:
        audit_results["checks"].append({"check": "Failure teaching preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Failure teaching preserves recoverability", "status": "FAIL"})

    # 5. First-Hour Smoke Test
    smoke_res = om.run_first_hour_smoke_test("survivor_smoke")
    if smoke_res["verdict"] == "UX_SUCCESS":
        audit_results["checks"].append({"check": "First-hour smoke test preserves engagement and clarity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "First-hour smoke test preserves engagement and clarity", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "survivor_entry_sequence_result.json"), 'w') as f:
        json.dump(profile, f, indent=2)
    with open(os.path.join(output_dir, "first_hour_smoke_test_result.json"), 'w') as f:
        json.dump(smoke_res, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("onboarding status")
    if "Survivor Onboarding Status" in res and "onboarding_profile_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports onboarding state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports onboarding state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_061_onboarding_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Onboarding validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_onboarding_validation()
