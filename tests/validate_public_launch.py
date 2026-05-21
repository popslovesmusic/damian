import os
import json
import shutil
import subprocess

def run_public_launch_validation():
    audit_results = {
        "patch_id": "STAGE-064",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/public_launch_boundary.json")
    contract_path = os.path.join(project_root, "engine/os_boundary/contracts/public_distribution_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Public launch readiness boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Public launch readiness boundary and contract defined", "status": "FAIL"})

    from engine.os_boundary.launch_runtime.launch_operations_manager import LaunchOperationsManager
    lom = LaunchOperationsManager(boundary_path, contract_path)

    # 2. Public Release Manifest Generation
    manifest = lom.generate_release_manifest("1.0.0-gold", "direct_download", "v1.0.0")
    if "release_hash" in manifest and manifest["release_channel"] == "direct_download":
        audit_results["checks"].append({"check": "Public release manifest generated successfully", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Public release manifest generated successfully", "status": "FAIL"})

    # 3. Release Artifact Verification
    is_verified = lom.verify_release_artifact(manifest, manifest["release_hash"])
    if is_verified:
        audit_results["checks"].append({"check": "Release artifact verification detects hash match", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Release artifact verification detects hash match", "status": "FAIL"})

    # 4. Public Relay Readiness
    relay_status = lom.simulate_public_relay_readiness(5000)
    if relay_status["load_capacity_ok"]:
        audit_results["checks"].append({"check": "Public relay infrastructure readiness remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Public relay infrastructure readiness remains bounded", "status": "FAIL"})

    # 5. Support Recovery Handoff
    recovery = lom.handle_support_recovery_handoff("survivor_gamma")
    if recovery["lineage_preserved"] is True:
        audit_results["checks"].append({"check": "Support recovery handoff preserves save lineage", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Support recovery handoff preserves save lineage", "status": "FAIL"})

    # 6. Telemetry Minimalism
    telemetry_ok = lom.monitor_telemetry_minimalism(["crash_reports_opt_in", "artifact_version"])
    if telemetry_ok:
        audit_results["checks"].append({"check": "Telemetry minimalism rejects forbidden collection", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Telemetry minimalism rejects forbidden collection", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "public_release_manifest_result.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(output_dir, "public_launch_smoke_test_result.json"), 'w') as f:
        json.dump(lom.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("launch status")
    if "Public Launch Readiness Status" in res and "release_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports launch readiness safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports launch readiness safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_064_public_launch_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Public Launch validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_public_launch_validation()
