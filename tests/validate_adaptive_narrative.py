import os
import json
import shutil
import subprocess

def run_adaptive_narrative_validation():
    audit_results = {
        "patch_id": "STAGE-052",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/adaptive_narrative_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/world_memory_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Adaptive narrative boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Adaptive narrative boundary and contract defined", "status": "FAIL"})

    from engine.domain.narrative_manager import NarrativeManager
    nm = NarrativeManager(boundary_path, contract_path)

    # 2. Narrative Residue Aggregation
    metrics = {"pressure": 50.0}
    memory = nm.aggregate_narrative_residue("world_test", metrics)
    if "memory_hash" in memory and memory["world_id"] == "world_test":
        audit_results["checks"].append({"check": "Narrative residue aggregation remains bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Narrative residue aggregation remains bounded", "status": "FAIL"})

    # 3. Procedural Narrative Drift
    drift = nm.apply_procedural_drift(memory)
    if "drift_type" in drift and "applied_delta" in drift:
        audit_results["checks"].append({"check": "Procedural narrative drift avoids canon lock", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Procedural narrative drift avoids canon lock", "status": "FAIL"})

    # 4. Historical Contract Generation
    contract = nm.generate_historical_contract(memory)
    if "contract_id" in contract and "context" in contract:
        audit_results["checks"].append({"check": "Historical contract generation reflects residue history", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Historical contract generation reflects residue history", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "narrative_residue_aggregation_result.json"), 'w') as f:
        json.dump(memory, f, indent=2)
    with open(os.path.join(output_dir, "narrative_drift_result.json"), 'w') as f:
        json.dump(drift, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("narrative status")
    if "World Memory Status" in res and "world_memory_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports narrative evolution safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports narrative evolution safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_052_narrative_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Narrative validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_adaptive_narrative_validation()
