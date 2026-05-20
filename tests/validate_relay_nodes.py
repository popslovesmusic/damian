import os
import json
import shutil
import subprocess

def run_relay_node_validation():
    audit_results = {
        "patch_id": "STAGE-044",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/network/contracts/relay_node_boundary.json")
    contract_path = os.path.join(project_root, "engine/network/contracts/relay_hub_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Relay node boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay node boundary and contract defined", "status": "FAIL"})

    from engine.network.runtime.relay_hub_stub import RelayHubManager
    rhm = RelayHubManager(boundary_path, contract_path)

    # 2. Hub Creation
    hub = rhm.create_relay_hub("survivor_test")
    if "relay_hash" in hub and hub["hub_operator_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Distributed survivor hub stub produces bounded relay", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Distributed survivor hub stub produces bounded relay", "status": "FAIL"})

    # 3. Async Relay Queue
    rhm.queue_message(hub, "domain_echo", {"id": "echo_001"})
    if len(hub["domain_echo_queue"]) > 0 and hub["bounded_flags"]["asynchronous_only"]:
        audit_results["checks"].append({"check": "Relay queue remains asynchronous", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay queue remains asynchronous", "status": "FAIL"})

    # 4. Visibility & Attention Tradeoff
    initial_p = hub["tower_attention_pressure"]
    rhm.queue_message(hub, "treaty_signal", {"id": "sig_001"})
    if hub["tower_attention_pressure"] > initial_p:
        audit_results["checks"].append({"check": "Relay visibility increases tower attention", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay visibility increases tower attention", "status": "FAIL"})

    # 5. Fragmentation Recovery
    hub["tower_attention_pressure"] = 100.0
    rhm.resolve_fragmentation(hub)
    if hub["fragmentation_state"] == "PARTIALLY_OFFLINE":
        audit_results["checks"].append({"check": "Relay fragmentation preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Relay fragmentation preserves recoverability", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "distributed_survivor_hub_result.json"), 'w') as f:
        json.dump(hub, f, indent=2)
    with open(os.path.join(output_dir, "relay_visibility_result.json"), 'w') as f:
        json.dump(rhm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("relay status")
    if "Relay Hub Status" in res and "relay_hub_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports relay status safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports relay status safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_044_relay_nodes_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Relay Node validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_relay_node_validation()
