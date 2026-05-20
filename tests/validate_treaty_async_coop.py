import os
import json
import shutil
import subprocess

def run_treaty_coop_validation():
    audit_results = {
        "patch_id": "STAGE-041",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/treaty_boundary.json")
    schema_path = os.path.join(project_root, "engine/domain/contracts/treaty_contract_schema.json")
    policy_path = os.path.join(project_root, "engine/domain/contracts/treaty_policy_contract.json")

    # 1. Boundary & Contract Checks
    all_exist = all(os.path.exists(p) for p in [boundary_path, schema_path, policy_path])
    if all_exist:
        audit_results["checks"].append({"check": "Treaty boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Treaty boundary and contracts defined", "status": "FAIL"})

    from engine.domain.treaty_manager import TreatyManager
    tm = TreatyManager(boundary_path, schema_path, policy_path)

    # 2. Treaty Creation Stub
    treaty = tm.create_treaty("player_alpha", ["player_alpha", "player_beta"], "The High Pass Accord")
    if "treaty_hash" in treaty and treaty["treaty_status"] == "ACTIVE":
        audit_results["checks"].append({"check": "Treaty creation stub produces bounded treaty", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Treaty creation stub produces bounded treaty", "status": "FAIL"})

    # 3. Shared Pressure Tradeoffs
    base_p = 100
    escalated = tm.resolve_shared_pressure(treaty, base_p)
    if escalated > base_p:
        audit_results["checks"].append({"check": "Shared pressure tradeoffs preserved", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Shared pressure tradeoffs preserved", "status": "FAIL"})

    # 4. Joint Defense Echo
    dummy_echo = {"defense_profile": {"base_defense": 10}}
    enhanced = tm.generate_joint_defense_echo(treaty, dummy_echo)
    if enhanced["defense_profile"]["base_defense"] > dummy_echo["defense_profile"]["base_defense"]:
        audit_results["checks"].append({"check": "Joint defense echo stub preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Joint defense echo stub preserves recoverability", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "treaty_creation_stub_result.json"), 'w') as f:
        json.dump(treaty, f, indent=2)
    with open(os.path.join(output_dir, "shared_reward_burden_result.json"), 'w') as f:
        json.dump(tm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("treaty status")
    if "Active Treaty Status" in res and "treaty_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports treaty state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports treaty state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_041_treaty_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Treaty validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_treaty_coop_validation()
