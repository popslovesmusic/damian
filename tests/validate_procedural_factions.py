import os
import json
import shutil
import subprocess

def run_faction_validation():
    audit_results = {
        "patch_id": "STAGE-048",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/faction_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/survivor_bloc_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Procedural faction boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Procedural faction boundary and contract defined", "status": "FAIL"})

    from engine.domain.faction_manager import FactionManager
    fm = FactionManager(boundary_path, contract_path)

    # 2. Faction Emergence
    members = ["s1", "s2", "s3", "s4", "s5"]
    bloc = fm.detect_faction_emergence("treaty_cluster", members, "STABILIZATION_PROFILE")
    if "bloc_hash" in bloc and bloc["emergence_source"] == "treaty_cluster":
        audit_results["checks"].append({"check": "Faction emergence stub creates bounded bloc", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Faction emergence stub creates bounded bloc", "status": "FAIL"})

    # 3. Stability and Fracture
    initial_attention = bloc["tower_attention_pressure"]
    fm.update_stability(bloc, 30.0) # High activity
    if bloc["tower_attention_pressure"] > initial_attention:
        audit_results["checks"].append({"check": "Faction growth increases tower attention", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Faction growth increases tower attention", "status": "FAIL"})

    fm.resolve_fracture(bloc)
    if "fracture_state" in bloc:
        audit_results["checks"].append({"check": "Faction fracture remain recoverable", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Faction fracture remain recoverable", "status": "FAIL"})

    # 4. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "faction_emergence_result.json"), 'w') as f:
        json.dump(bloc, f, indent=2)
    with open(os.path.join(output_dir, "faction_stability_fracture_result.json"), 'w') as f:
        json.dump(fm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("faction status")
    if "Survivor Bloc Status" in res and "bloc_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports faction state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports faction state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_048_faction_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Faction validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_faction_validation()
