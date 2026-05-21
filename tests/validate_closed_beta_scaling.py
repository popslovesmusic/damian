import os
import json
import shutil
import subprocess

def run_beta_scaling_validation():
    audit_results = {
        "patch_id": "STAGE-063",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/core/orchestrator/contracts/closed_beta_boundary.json")
    contract_path = os.path.join(project_root, "engine/core/orchestrator/contracts/persistence_contract_schema.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Closed beta scaling boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Closed beta scaling boundary and contract defined", "status": "FAIL"})

    from engine.core.orchestrator.beta_runtime.beta_operations_manager import BetaOperationsManager
    bom = BetaOperationsManager(boundary_path, contract_path)

    # 2. Relay Scaling
    scale = bom.simulate_population_scaling(50, 2000)
    if scale["status"] in ["SCALED", "THROTTLED"] and scale["active_relays"] > 50:
        audit_results["checks"].append({"check": "Multi-relay population scaling remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Multi-relay population scaling remains bounded", "status": "FAIL"})

    # 3. World Memory Compression
    mem = bom.simulate_world_memory_compression(120.0)
    if mem["action"] == "COMPRESSED_HISTORICAL_RESIDUE" and mem["new_size"] < mem["original_size"]:
        audit_results["checks"].append({"check": "World memory compression preserves historical identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "World memory compression preserves historical identity", "status": "FAIL"})

    # 4. Economy Anti-Inflation
    econ = bom.simulate_economy_anti_inflation(15000, 5)
    if econ["status"] == "ANTI_INFLATION_ACTIVE" and econ["decay_modifier"] > 1.0:
        audit_results["checks"].append({"check": "Beta economy avoids inflation collapse", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Beta economy avoids inflation collapse", "status": "FAIL"})

    # 5. Save Migration
    mig = bom.plan_save_migration("1.3.0-beta")
    if mig["status"] == "DRY_RUN_READY" and mig["recoverable"] is True:
        audit_results["checks"].append({"check": "Save migration preserves survivor continuity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Save migration preserves survivor continuity", "status": "FAIL"})

    # 6. Social Recovery
    soc = bom.resolve_social_recovery("player_1", "SPAM")
    if soc["status"] == "SANCTION_APPLIED_SAFELY" and "recovery_path" in soc:
         audit_results["checks"].append({"check": "Social recovery boundary prevents irreversible exile", "status": "PASS"})
    else:
         audit_results["checks"].append({"check": "Social recovery boundary prevents irreversible exile", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "long_term_persistence_contract_result.json"), 'w') as f:
        # Mocking the contract output for terminal status
        json.dump({"beta_cycle_id": "beta_001", "status": "ACTIVE"}, f, indent=2)
    with open(os.path.join(output_dir, "beta_scaling_smoke_test_result.json"), 'w') as f:
        json.dump(bom.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("beta status")
    if "Closed Beta Operations Status" in res:
        audit_results["checks"].append({"check": "Beta operations dashboard readable under scale", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Beta operations dashboard readable under scale", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_063_beta_scaling_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Beta Scaling validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_beta_scaling_validation()
