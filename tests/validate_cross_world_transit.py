import os
import json
import shutil
import subprocess

def run_cross_world_transit_validation():
    audit_results = {
        "patch_id": "STAGE-043",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/cross_world_transit_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/identity_continuity_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Cross-world transit boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Cross-world transit boundary and contracts defined", "status": "FAIL"})

    from engine.domain.transit_manager import TransitManager
    tm = TransitManager(boundary_path, contract_path)

    # 2. Survivor Transit Export
    profile = {"residue": {"signature": "alpha", "weight": 100}, "reputation": {"score": 85}}
    export = tm.export_survivor("survivor_test", "damian", "jacobs_bane", profile)
    if "transit_hash" in export and export["survivor_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Survivor transit export stub produces hash-verifiable export", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Survivor transit export stub produces hash-verifiable export", "status": "FAIL"})

    # 3. Residue Translation
    translated = tm.translate_residue(profile["residue"], "jacobs_bane")
    if "translated_weight" in translated and translated["translated_weight"] < profile["residue"]["weight"]:
        audit_results["checks"].append({"check": "Residue translation preserves continuity safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Residue translation preserves continuity safely", "status": "FAIL"})

    # 4. Inventory Echo Boundary
    items = [{"id": "item_1", "type": "symbolic_inventory_echo"}, {"id": "item_2", "type": "os_level_artifact"}]
    validated = tm.validate_inventory_echo(items)
    if len(validated) == 1 and validated[0]["id"] == "item_1":
        audit_results["checks"].append({"check": "Inventory echo boundary prevents unrestricted transfer", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Inventory echo boundary prevents unrestricted transfer", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store export for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "survivor_transit_export_result.json"), 'w') as f:
        json.dump(export, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("transit status")
    if "Cross-World Transit Status" in res and "transit_hash" in res:
        audit_results["checks"].append({"check": "Admin terminal reports cross-world transit safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports cross-world transit safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_043_cross_world_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Cross-World validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_cross_world_transit_validation()
