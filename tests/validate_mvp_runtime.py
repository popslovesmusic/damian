import os
import json
import shutil
import subprocess

def run_mvp_runtime_validation():
    audit_results = {
        "patch_id": "STAGE-050",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/core/orchestrator/contracts/vertical_slice_boundary.json")
    contract_path = os.path.join(project_root, "engine/core/orchestrator/contracts/gameplay_loop_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Vertical slice boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Vertical slice boundary and contract defined", "status": "FAIL"})

    from engine.core.orchestrator.mvp_runtime_orchestrator import MvpRuntimeOrchestrator
    mo = MvpRuntimeOrchestrator(data_root, boundary_path, contract_path)

    # 2. Run Full Smoke Test
    result = mo.run_full_smoke_test()
    if result["verdict"] == "PASS":
        audit_results["checks"].append({"check": "Runtime smoke-test scenario passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Runtime smoke-test scenario passes", "status": "FAIL"})

    # Detailed flow checks based on the orchestrator's evidence
    steps = [s["step"] for s in result["completed_flow_steps"]]
    
    if "initialize_survivor_identity" in steps and "enter_tower" in steps:
        audit_results["checks"].append({"check": "Survivor onboarding and entry flow pass", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Survivor onboarding and entry flow pass", "status": "FAIL"})

    if "publish_domain_echo" in steps and "create_or_join_treaty" in steps:
        audit_results["checks"].append({"check": "Core social loops integrated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Core social loops integrated", "status": "FAIL"})
        
    if "respond_to_event_wave_pressure" in steps:
        audit_results["checks"].append({"check": "Event pressure runtime integrated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Event pressure runtime integrated", "status": "FAIL"})
        
    if "resume_from_persistent_state" in steps:
        audit_results["checks"].append({"check": "Persistent resume runtime passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Persistent resume runtime passes", "status": "FAIL"})

    # 3. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    
    audit_path = os.path.join(output_dir, "mvp_runtime_smoke_test_result.json")
    mo.emit_audit(audit_path)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("mvp audit")
    if "MVP Runtime Smoke Test Audit" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports MVP runtime safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports MVP runtime safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_050_mvp_runtime_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"MVP Runtime validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_mvp_runtime_validation()
