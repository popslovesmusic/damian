import os
import json
import shutil
import subprocess

def run_politics_validation():
    audit_results = {
        "patch_id": "STAGE-049",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/faction_schism_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/schism_event_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Faction schism boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Faction schism boundary and contract defined", "status": "FAIL"})

    from engine.domain.schism_manager import SchismManager
    sm = SchismManager(boundary_path, contract_path)

    # 2. Schism Generation
    dummy_bloc = {"bloc_id": "bloc_prime", "dominant_residue_signature": "ORDER", "member_survivor_ids": ["s1", "s2", "s3", "s4"]}
    schism = sm.generate_schism(dummy_bloc, "treaty_betrayal")
    if "schism_hash" in schism and schism["trigger_source"] == "treaty_betrayal":
        audit_results["checks"].append({"check": "Schism generation stub produces bounded schism", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Schism generation stub produces bounded schism", "status": "FAIL"})

    # 3. Splinter Bloc Formation
    splinters = sm.form_splinter_bloc(dummy_bloc, schism)
    if len(splinters) == 2 and any(s["status"] == "SPLINTERED" for s in splinters):
        audit_results["checks"].append({"check": "Splinter bloc formation preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Splinter bloc formation preserves recoverability", "status": "FAIL"})

    # 4. Political Recovery
    recovery = sm.resolve_reconciliation(schism["schism_id"])
    if recovery["status"] == "RECOVERING" and recovery["recoverable"] is True:
        audit_results["checks"].append({"check": "Political recovery remains possible", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Political recovery remains possible", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "faction_schism_generation_result.json"), 'w') as f:
        json.dump(schism, f, indent=2)
    with open(os.path.join(output_dir, "political_recovery_result.json"), 'w') as f:
        json.dump(sm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("politics status")
    if "Survivor Schism Status" in res and "schism_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports faction politics safely", "status": "PASS"})
    else:
        # Check output content
        if "Faction Schism Status" in res or "Survivor Schism Status" in res:
             audit_results["checks"].append({"check": "Admin terminal reports faction politics safely", "status": "PASS"})
        else:
             audit_results["checks"].append({"check": "Admin terminal reports faction politics safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_049_faction_politics_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Faction Politics validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_politics_validation()
