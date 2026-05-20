import os
import json
import shutil
import subprocess

def run_domain_echo_validation():
    audit_results = {
        "patch_id": "STAGE-039",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/domain_echo_pvp_boundary.json")
    snapshot_contract_path = os.path.join(project_root, "engine/domain/contracts/domain_echo_snapshot_contract.json")
    resolution_path = os.path.join(project_root, "engine/domain/contracts/offline_attack_resolution_boundary.json")

    # 1. Boundary & Contract Checks
    all_exist = all(os.path.exists(p) for p in [boundary_path, snapshot_contract_path, resolution_path])
    if all_exist:
        audit_results["checks"].append({"check": "Domain echo PvP boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Domain echo PvP boundary and contracts defined", "status": "FAIL"})

    # 2. Export Stub
    from engine.domain.domain_echo_exporter import DomainEchoExporter
    exporter = DomainEchoExporter(snapshot_contract_path)
    dummy_dash = {"snapshot_id": "dash_test", "domain_claim_count": 3}
    echo = exporter.export_echo("player_test", dummy_dash)
    if "sha256" in echo and echo["owner_player_id"] == "player_test":
        audit_results["checks"].append({"check": "Domain echo export stub produces hash-verifiable snapshot", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Domain echo export stub produces hash-verifiable snapshot", "status": "FAIL"})

    # 3. Attack Stub
    from engine.domain.offline_attack_resolver import OfflineAttackResolver
    resolver = OfflineAttackResolver(resolution_path)
    attack_res = resolver.resolve_attack("attacker_test", echo)
    if attack_res["outcome"] in ["ATTACK_REPELLED", "ATTACK_PARTIAL_SUCCESS"]:
        audit_results["checks"].append({"check": "Offline attack stub produces bounded result", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Offline attack stub produces bounded result", "status": "FAIL"})

    # 4. Recoverability & Anti-Griefing
    if attack_res.get("recoverability_preserved") is True and attack_res.get("anti_griefing_clean") is True:
        audit_results["checks"].append({"check": "Owner recoverability and anti-griefing limits enforced", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Owner recoverability and anti-griefing limits enforced", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store attack result for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "offline_domain_attack_result.json"), 'w') as f:
        json.dump(attack_res, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("echo report")
    if "Domain Echo Attack Report" in res and "outcome" in res:
        audit_results["checks"].append({"check": "Admin terminal reports domain echo status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports domain echo status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_039_domain_echo_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Domain Echo validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_domain_echo_validation()
