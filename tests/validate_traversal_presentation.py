import os
import json
import shutil
import subprocess

def run_traversal_presentation_validation():
    audit_results = {
        "patch_id": "STAGE-057",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/traversal/contracts/traversal_boundary.json")
    contract_path = os.path.join(project_root, "engine/traversal/contracts/movement_contract_schema.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Traversal boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Traversal boundary and contract defined", "status": "FAIL"})

    from engine.traversal.runtime.movement_feel_manager import MovementFeelManager
    mfm = MovementFeelManager(boundary_path, contract_path)

    # 2. Movement Profile Generation
    p1 = mfm.generate_movement_profile("RUSH", 80, 50)
    if p1["visibility_modifier"] > 2.0 and p1["stamina_or_exhaustion_profile"]["movement_drag"] > 0:
        audit_results["checks"].append({"check": "Movement profile generation Communicates pressure", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Movement profile generation Communicates pressure", "status": "FAIL"})

    # 3. Route Exposure Tradeoffs
    if mfm.validate_route_exposure("route_1", 2.5): # High visibility
        audit_results["checks"].append({"check": "Route exposure boundary preserves tradeoffs", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Route exposure boundary preserves tradeoffs", "status": "FAIL"})

    # 4. Exhaustion Effects
    p2 = mfm.generate_movement_profile("CAUTIOUS", 10, 90) # High exhaustion
    if p2["camera_behavior_profile"]["tilt_angle"] > 0 and p2["audio_feedback_profile"]["breathing_intensity"] > 0.8:
         audit_results["checks"].append({"check": "Exhaustion movement affects traversal behavior", "status": "PASS"})
    else:
         audit_results["checks"].append({"check": "Exhaustion movement affects traversal behavior", "status": "FAIL"})

    # 5. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "movement_contract_result.json"), 'w') as f:
        json.dump(p1, f, indent=2)
    with open(os.path.join(output_dir, "traversal_boundary_result.json"), 'w') as f:
        json.dump(mfm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("traversal status")
    if "Movement Profile Status" in res and "movement_profile_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports traversal state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports traversal state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_057_traversal_presentation_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Traversal Presentation validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_traversal_presentation_validation()
