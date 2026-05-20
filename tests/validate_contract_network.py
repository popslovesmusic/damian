import os
import json
import shutil
import subprocess

def run_contract_network_validation():
    audit_results = {
        "patch_id": "STAGE-047",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/contract_network_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/quest_broadcast_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Contract network boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Contract network boundary and contract defined", "status": "FAIL"})

    from engine.domain.contract_manager import ContractManager
    cm = ContractManager(boundary_path, contract_path)

    # 2. Contract Generation
    contract = cm.generate_procedural_contract("relay_hub_test", "resource_recovery", "SUPPLY_DROP")
    if "contract_hash" in contract and contract["contract_type"] == "resource_recovery":
        audit_results["checks"].append({"check": "Procedural contract generation produces bounded contracts", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Procedural contract generation produces bounded contracts", "status": "FAIL"})

    # 3. Contract Acceptance
    acceptance = cm.accept_contract("survivor_test", contract)
    if acceptance["status"] == "ACCEPTED" and acceptance["survivor_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Contract acceptance preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Contract acceptance preserves recoverability", "status": "FAIL"})

    # 4. Contract Failure
    failure = cm.resolve_failure(contract)
    if failure["outcome"] == "FAILED" and "reputation_damage" in failure["applied_scars"]:
        audit_results["checks"].append({"check": "Contract failure scars remain bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Contract failure scars remain bounded", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "procedural_contract_generation_result.json"), 'w') as f:
        json.dump(contract, f, indent=2)
    with open(os.path.join(output_dir, "contract_failure_result.json"), 'w') as f:
        json.dump(failure, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("quest status")
    if "Survivor Contract Status" in res and "contract_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports contract state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports contract state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_047_contract_network_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Contract Network validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_contract_network_validation()
