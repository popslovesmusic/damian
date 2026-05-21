import os
import json
import shutil
import subprocess

def run_enemy_ecology_validation():
    audit_results = {
        "patch_id": "STAGE-058",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/enemies/contracts/enemy_ecology_boundary.json")
    contract_path = os.path.join(project_root, "engine/enemies/contracts/enemy_behavior_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Enemy ecology boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Enemy ecology boundary and contract defined", "status": "FAIL"})

    from engine.enemies.runtime.enemy_ecology_manager import EnemyEcologyManager
    em = EnemyEcologyManager(boundary_path, contract_path)

    # 2. Pressure-Reactive Spawn (Profile Generation)
    # High pressure, low route usage
    p1 = em.generate_enemy_profile("PRESSURE_FEEDER", 80, 10)
    if p1["mutation_profile"]["active"] is True and p1["pressure_response_profile"]["aggression_multiplier"] > 1.5:
        audit_results["checks"].append({"check": "Pressure-reactive spawn system responds to world state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Pressure-reactive spawn system responds to world state", "status": "FAIL"})

    # 3. Predator Migration (Route Overuse)
    routes = {"route_hot": 90, "route_cold": 10}
    log = em.resolve_predator_migration(routes)
    if len(log) == 1 and log[0]["route_id"] == "route_hot":
        audit_results["checks"].append({"check": "Route overuse changes predator migration", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Route overuse changes predator migration", "status": "FAIL"})

    # 4. Enemy Adaptation (Bounded and Readable)
    if p1["bounded_flags"]["readable"] is True and "enemy_hash" in p1:
        audit_results["checks"].append({"check": "Enemy adaptation remains bounded and readable", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Enemy adaptation remains bounded and readable", "status": "FAIL"})

    # 5. Threat Readability
    if em.validate_threat_readability(p1):
        audit_results["checks"].append({"check": "Threat readability boundary preserves telegraph clarity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Threat readability boundary preserves telegraph clarity", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "enemy_behavior_contract_result.json"), 'w') as f:
        json.dump(p1, f, indent=2)
    with open(os.path.join(output_dir, "enemy_ecology_boundary_result.json"), 'w') as f:
        json.dump(em.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("enemy status")
    if "Enemy Ecology Status" in res and "enemy_profile_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports enemy ecology safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports enemy ecology safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_058_enemy_ecology_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Enemy Ecology validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_enemy_ecology_validation()
