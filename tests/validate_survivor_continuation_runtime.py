import os
import json
import shutil
import subprocess

def run_survivor_continuation_validation():
    audit_results = {
        "patch_id": "STAGE-060",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/player/contracts/death_continuation_boundary.json")
    contract_path = os.path.join(project_root, "engine/player/contracts/survivor_continuation_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Death continuation boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Death continuation boundary and contract defined", "status": "FAIL"})

    from engine.player.runtime.continuation_manager import ContinuationManager
    cm = ContinuationManager(boundary_path, contract_path)

    # 2. Continuation Manifest Generation
    manifest = cm.generate_continuation_manifest("survivor_test", "death_001", "FALL_DAMAGE")
    if "continuation_hash" in manifest and manifest["survivor_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Defeat continuation stub preserves residue", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Defeat continuation stub preserves residue", "status": "FAIL"})

    # 3. Inheritance Bounding
    if manifest["inheritance_profile"].get("bounded_value") is True:
        audit_results["checks"].append({"check": "Inheritance carryover remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Inheritance carryover remains bounded", "status": "FAIL"})

    # 4. Legacy Recovery
    recovery = cm.resolve_legacy_recovery(manifest, "RECOVERY_RUN")
    if recovery["status"] == "SURVIVOR_RECOVERED" and recovery["identity_continuity"] is True:
        audit_results["checks"].append({"check": "Legacy recovery preserves survivor identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Legacy recovery preserves survivor identity", "status": "FAIL"})

    # 5. World Memory Update
    if cm.update_world_memory_after_death(manifest):
        audit_results["checks"].append({"check": "Death scar updates world memory", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Death scar updates world memory", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "survivor_continuation_contract_result.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(output_dir, "death_scar_world_memory_result.json"), 'w') as f:
        json.dump(cm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("continuation status")
    if "Survivor Continuation Status" in res and "continuation_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports continuation state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports continuation state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_060_survivor_continuation_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Survivor Continuation validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_survivor_continuation_validation()
