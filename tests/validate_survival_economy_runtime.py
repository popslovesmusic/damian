import os
import json
import shutil
import subprocess

def run_survival_economy_validation():
    audit_results = {
        "patch_id": "STAGE-059",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/economy/contracts/resource_scarcity_boundary.json")
    contract_path = os.path.join(project_root, "engine/economy/contracts/survival_economy_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Resource scarcity boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Resource scarcity boundary and contract defined", "status": "FAIL"})

    from engine.economy.runtime.survival_economy_manager import SurvivalEconomyManager
    sem = SurvivalEconomyManager(boundary_path, contract_path)

    # 2. Resource Distribution (Profile Generation)
    # High scarcity, high pressure
    r1 = sem.generate_resource_profile("FOOD", 9, 80)
    if r1["decay_profile"]["decay_rate"] > 0.01 and r1["visibility_profile"]["base_visibility"] > 1.5:
        audit_results["checks"].append({"check": "Resource distribution remains pressure-reactive", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Resource distribution remains pressure-reactive", "status": "FAIL"})

    # 3. Resource Decay
    if r1["decay_profile"]["is_perishable"] is True:
        audit_results["checks"].append({"check": "Resource decay introduces instability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Resource decay introduces instability", "status": "FAIL"})

    # 4. Scavenging Pressure
    log = sem.apply_scavenging_pressure("survivor_test", 5000, 20)
    if log["visibility_increase"] > 0 and "success" in log:
        audit_results["checks"].append({"check": "Scavenging runtime increases exposure risk", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Scavenging runtime increases exposure risk", "status": "FAIL"})

    # 5. Improvised Crafting
    craft = sem.resolve_improvised_crafting("TOOLS", 70)
    if craft["quality_score"] < 1.0 and craft["is_imperfect"] is True:
        audit_results["checks"].append({"check": "Improvised crafting remains viable but imperfect", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Improvised crafting remains viable but imperfect", "status": "FAIL"})

    # 6. Inventory Weight
    if r1["weight_profile"]["unit_weight"] > 0 and r1["bounded_flags"]["weight_coupled"]:
        audit_results["checks"].append({"check": "Inventory weight affects traversal and escape", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Inventory weight affects traversal and escape", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "survival_economy_contract_result.json"), 'w') as f:
        json.dump(r1, f, indent=2)
    with open(os.path.join(output_dir, "resource_distribution_result.json"), 'w') as f:
        json.dump(sem.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("economy status")
    if "Survival Economy Status" in res and "resource_profile_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports economy state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports economy state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_059_survival_economy_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Survival Economy validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_survival_economy_validation()
