import os
import json
import shutil
import subprocess

def run_infinite_sustainability_validation():
    audit_results = {
        "patch_id": "STAGE-066",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/core/orchestrator/contracts/infinite_sustainability_boundary.json")
    contract_path = os.path.join(project_root, "engine/core/orchestrator/contracts/narrative_saturation_contract_schema.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Infinite sustainability boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Infinite sustainability boundary and contract defined", "status": "FAIL"})

    from engine.core.orchestrator.long_term_runtime.infinite_sustainability_manager import InfiniteSustainabilityManager
    ism = InfiniteSustainabilityManager(boundary_path, contract_path)

    # 2. Recursive Content Mutation
    content_report = ism.recursively_mutate_content("CORE_ASSET_A", 3)
    if content_report["final_coherence_score"] >= 0.5 and content_report["lineage_traceable"] is True:
        audit_results["checks"].append({"check": "Recursive content mutation preserves coherence", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Recursive content mutation preserves coherence", "status": "FAIL"})

    # 3. Historical Myth Compression
    myth_report = ism.compress_historical_myth_layers(250)
    if myth_report["key_myths_preserved"] is True and myth_report["narrative_lineage_intact"] is True:
        audit_results["checks"].append({"check": "Historical myth compression preserves identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Historical myth compression preserves identity", "status": "FAIL"})

    # 4. Anti-Stagnation Mechanisms
    meta_report = ism.prevent_meta_stagnation(0.9)
    if meta_report["intervention_applied"] == "ACTIVE_REBALANCING" and meta_report["gameplay_freshness_maintained"] is True:
        audit_results["checks"].append({"check": "Anti-stagnation systems prevent permanent meta lock", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Anti-stagnation systems prevent permanent meta lock", "status": "FAIL"})

    # 5. Relay Civilization Drift
    relay_drift_report = ism.evolve_relay_civilization_drift(0.7)
    if relay_drift_report["identity_preserved"] is True and relay_drift_report["recoverable_changes"] is True:
        audit_results["checks"].append({"check": "Relay civilization drift remains recoverable", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay civilization drift remains recoverable", "status": "FAIL"})
        
    # 6. Infinite Sustainability Smoke Test
    smoke_test_log = ism.simulate_infinite_sustainability_smoke_test(60)
    if smoke_test_log["overall_verdict"] == "SUSTAINABILITY_OPTIMAL":
        audit_results["checks"].append({"check": "Infinite sustainability smoke test preserves coherence", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Infinite sustainability smoke test preserves coherence", "status": "FAIL"})


    # 7. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "narrative_saturation_contract_result.json"), 'w') as f:
        json.dump(ism.trigger_sustainability_cycle("ETERNAL_TEST_CYCLE", 50), f, indent=2)
    with open(os.path.join(output_dir, "infinite_sustainability_smoke_test_result.json"), 'w') as f:
        json.dump(ism.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("sustain status")
    if "Infinite Tower Sustainability Status" in res and "sustainability_hash" in res:
        audit_results["checks"].append({"check": "Admin terminal reports sustainability status safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports sustainability status safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_066_infinite_sustainability_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Infinite Sustainability validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_infinite_sustainability_validation()
