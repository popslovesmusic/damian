import os
import json
import shutil
import subprocess

def run_alpha_stress_validation():
    audit_results = {
        "patch_id": "STAGE-051-STRESS",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/closed_alpha_boundary.json")
    stress_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/stress_test_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(stress_contract_path):
        audit_results["checks"].append({"check": "Alpha boundary and stress contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Alpha boundary and stress contract defined", "status": "FAIL"})

    from engine.os_boundary.alpha_stress_manager import AlphaStressManager
    asm = AlphaStressManager(boundary_path, stress_contract_path)

    # 2. Enrollment
    enrollment = asm.enroll_survivors(["s1", "s2", "s3", "s4", "s5"])
    if enrollment["status"] == "ENROLLED" and enrollment["enrolled_count"] == 5:
        audit_results["checks"].append({"check": "Alpha enrollment stub produces bounded pool", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Alpha enrollment stub produces bounded pool", "status": "FAIL"})

    # 3. Session Stress Simulation
    stress = asm.simulate_session_stress(10, 2.5)
    if stress["recoverability_verified"] is True and stress["load_multiplier"] == 2.5:
        audit_results["checks"].append({"check": "Session stress simulation preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Session stress simulation preserves recoverability", "status": "FAIL"})

    # 4. Echo Saturation
    saturation = asm.simulate_echo_saturation(100)
    if saturation["recoverability_preserved"] is True and saturation["total_attacks"] == 100:
        audit_results["checks"].append({"check": "Domain echo saturation remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Domain echo saturation remains bounded", "status": "FAIL"})

    # 5. Retention Metrics
    metrics = asm.capture_retention_metrics()
    if metrics["persistence_integrity_rate"] == 1.0:
        audit_results["checks"].append({"check": "Retention metrics remain contextual", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Retention metrics remain contextual", "status": "FAIL"})

    # 6. Stress Test Audit
    audit = asm.generate_stress_test_audit("alpha_stress_001")
    if "stress_hash" in audit and audit["stress_test_id"] == "alpha_stress_001":
        audit_results["checks"].append({"check": "Failure and recovery audit captures lineage", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Failure and recovery audit captures lineage", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "retention_metrics_result.json"), 'w') as f:
        json.dump(metrics, f, indent=2)
    with open(os.path.join(output_dir, "stress_test_contract_result.json"), 'w') as f:
        json.dump(audit, f, indent=2)
    with open(os.path.join(output_dir, "alpha_cohort_result.json"), 'w') as f:
        json.dump(enrollment, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("alpha audit")
    if "Stress Test Audit" in res and "stress_hash" in res:
        audit_results["checks"].append({"check": "Admin terminal reports alpha runtime safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports alpha runtime safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_051_alpha_stress_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Alpha Stress validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_alpha_stress_validation()
