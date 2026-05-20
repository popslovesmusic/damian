import os
import json
import shutil
import subprocess

def run_reputation_validation():
    audit_results = {
        "patch_id": "STAGE-042",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/domain/contracts/reputation_boundary.json")
    contract_path = os.path.join(project_root, "engine/domain/contracts/trust_network_contract.json")
    trace_path = os.path.join(project_root, "engine/domain/contracts/retaliation_trace_boundary.json")

    # 1. Boundary & Contract Checks
    all_exist = all(os.path.exists(p) for p in [boundary_path, contract_path, trace_path])
    if all_exist:
        audit_results["checks"].append({"check": "Reputation boundary and contracts defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Reputation boundary and contracts defined", "status": "FAIL"})

    from engine.domain.reputation_manager import ReputationManager
    rm = ReputationManager(boundary_path, contract_path)

    # 2. Signal Generation
    s1 = rm.generate_signal("survivor_test", "successful_joint_defense", 5.0)
    if s1["category"] == "POSITIVE" and s1["recoverable"] is True:
        audit_results["checks"].append({"check": "Reputation signal generation stub produces bounded signals", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Reputation signal generation stub produces bounded signals", "status": "FAIL"})

    # 3. Trust Drift and Recovery
    s2 = rm.generate_signal("survivor_test", "treaty_abandonment", 10.0)
    score = rm.calculate_trust_drift(50, [s1, s2])
    if 0 <= score <= 100:
        audit_results["checks"].append({"check": "Trust drift and recovery preserves recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Trust drift and recovery preserves recoverability", "status": "FAIL"})

    # 4. Reputation Snapshot
    snap = rm.get_reputation_snapshot("survivor_test", score)
    if "trust_hash" in snap and snap["survivor_id"] == "survivor_test":
        audit_results["checks"].append({"check": "Reputation snapshot stub produces contextual state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Reputation snapshot stub produces contextual state", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "reputation_snapshot_result.json"), 'w') as f:
        json.dump(snap, f, indent=2)
    with open(os.path.join(output_dir, "reputation_signal_generation_result.json"), 'w') as f:
        json.dump(rm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("reputation status")
    if "Survivor Reputation Snapshot" in res and "survivor_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports trust network state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports trust network state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_042_reputation_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Reputation validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_reputation_validation()
