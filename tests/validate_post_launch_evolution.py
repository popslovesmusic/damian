import os
import json
import shutil
import subprocess

def run_post_launch_evolution_validation():
    audit_results = {
        "patch_id": "STAGE-065",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/core/orchestrator/contracts/post_launch_evolution_boundary.json")
    contract_path = os.path.join(project_root, "engine/core/orchestrator/contracts/seasonal_mutation_contract_schema.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Post-launch evolution boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Post-launch evolution boundary and contract defined", "status": "FAIL"})

    from engine.core.orchestrator.post_launch_runtime.post_launch_manager import PostLaunchManager
    plm = PostLaunchManager(boundary_path, contract_path)

    # 2. World Mutation Cycle Trigger
    mutation_profile = plm.trigger_world_mutation_cycle("SUMMER_BLIGHT", 70)
    if "mutation_hash" in mutation_profile and mutation_profile["bounded_flags"]["identity_preserved"] is True:
        audit_results["checks"].append({"check": "World mutation runtime preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "World mutation runtime preserves recoverability", "status": "FAIL"})

    # 3. Historical Layer Compression
    historical_report = plm.compress_historical_layers(800)
    if historical_report["action"] == "DEEP_COMPRESSION" and historical_report["lineage_integrity_score"] >= 0.8:
        audit_results["checks"].append({"check": "Historical compression preserves lineage", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Historical compression preserves lineage", "status": "FAIL"})

    # 4. Relay Ecosystem Evolution
    relay_report = plm.evolve_relay_ecosystem(150, 80)
    if relay_report["new_relay_count"] > 150 and relay_report["recoverable_restructuring"] is True:
        audit_results["checks"].append({"check": "Relay ecosystem evolution remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay ecosystem evolution remains bounded", "status": "FAIL"})

    # 5. Survivor Legacy Preservation
    legacy_record = plm.preserve_survivor_legacy("survivor_zeta", ["SEASONAL_VICTORY"])
    if legacy_record["identity_continuity_score"] >= 0.99:
        audit_results["checks"].append({"check": "Survivor legacy preservation remains visible", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Survivor legacy preservation remains visible", "status": "FAIL"})

    # 6. Tower Evolution Smoke Test
    smoke_test_log = plm.simulate_tower_evolution_smoke_test(75)
    if smoke_test_log["overall_status"] == "EVOLUTION_NOMINAL":
        audit_results["checks"].append({"check": "Tower evolution smoke test preserves continuity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Tower evolution smoke test preserves continuity", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "seasonal_mutation_contract_result.json"), 'w') as f:
        json.dump(mutation_profile, f, indent=2)
    with open(os.path.join(output_dir, "tower_evolution_smoke_test_result.json"), 'w') as f:
        json.dump(plm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("evolution status")
    if "Tower Evolution Status" in res and "cycle_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports post-launch evolution safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports post-launch evolution safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_065_post_launch_evolution_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Post-Launch Evolution validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_post_launch_evolution_validation()
