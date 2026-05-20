import os
import json
import shutil
import subprocess

def run_update_cartridge_validation():
    audit_results = {
        "patch_id": "STAGE-038",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/update_cartridge_boundary.json")
    manifest_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/update_cartridge_manifest_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(manifest_contract_path):
        audit_results["checks"].append({"check": "Update boundary and manifest contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Update boundary and manifest contract defined", "status": "FAIL"})

    from engine.os_boundary.update_manager import UpdateManager
    um = UpdateManager(data_root, boundary_path, manifest_contract_path)

    # 2. Update Cartridge Verification
    dummy_manifest = {
        "update_id": "TOWER_UPDATE_PROTO_001",
        "version_target": "1.1.0",
        "version_source_min": "1.0.0",
        "release_date": "2026-05-20",
        "patch_payloads": ["delta.img"],
        "sha256_root_hash": "abc123hash",
        "rollback_support": True,
        "admin_approval_phrase": "APPROVE_PROTO_UPDATE"
    }
    manifest_path = os.path.join(data_root, "test_update_manifest.json")
    with open(manifest_path, 'w') as f: json.dump(dummy_manifest, f)
    
    if um.verify_cartridge(manifest_path, data_root):
        audit_results["checks"].append({"check": "Update cartridge verification passes (Success case)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Update cartridge verification passes (Success case)", "status": "FAIL"})

    # 3. Patch Migration Dry-Run
    plan = um.generate_migration_dry_run(dummy_manifest)
    if plan["verdict"] == "DRY_RUN_SUCCESS" and len(plan["steps"]) > 0:
        audit_results["checks"].append({"check": "Patch migration dry-run planner generated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Patch migration dry-run planner generated", "status": "FAIL"})

    # 4. Backup Before Update Gate
    if um.create_pre_update_backup("TOWER_UPDATE_PROTO_001"):
        audit_results["checks"].append({"check": "Backup before update gate enforced", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Backup before update gate enforced", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal to read
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    um.emit_audit(os.path.join(output_dir, "update_cartridge_verification_result.json"))

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("update audit")
    if "Update Artifact Audit" in res and "verification" in res:
        audit_results["checks"].append({"check": "Admin terminal reports update lineage evidence", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports update lineage evidence", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_038_update_cartridge_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Update Cartridge validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_update_cartridge_validation()
