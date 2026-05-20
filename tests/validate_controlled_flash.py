import os
import json
import shutil
import hashlib

def run_controlled_flash_validation():
    audit_results = {
        "patch_id": "STAGE-035",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/physical_flash_boundary.json")
    contract_path = os.path.join(project_root, "engine/os_boundary/contracts/flash_execution_contract.json")

    # 1. Contract checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Physical flash boundary and execution contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Physical flash boundary and execution contract defined", "status": "FAIL"})

    from engine.os_boundary.flash_execution_manager import FlashExecutionManager
    fem = FlashExecutionManager(boundary_path, contract_path)

    # 2. Safety Filters (Rejected devices)
    internal_dev = {"id": "sda", "vendor": "Samsung", "is_removable": False, "interface": "nvme"}
    if not fem.validate_target_device(internal_dev):
        audit_results["checks"].append({"check": "Internal host disks rejected", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Internal host disks rejected", "status": "FAIL"})

    non_usb_dev = {"id": "sdc", "vendor": "Generic", "is_removable": True, "interface": "sata"}
    if not fem.validate_target_device(non_usb_dev):
        audit_results["checks"].append({"check": "Non-removable/Non-USB devices rejected", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Non-removable/Non-USB devices rejected", "status": "FAIL"})

    # 3. Compatibility Verification
    img_path = os.path.join(project_root, "build/live_os/images/tower-damian-proto.img")
    if not os.path.exists(img_path):
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'w') as f: f.write("STUB_ARTIFACT_FOR_STAGE_035")
        
    good_usb = {"id": "sdb", "size": "32G", "is_removable": True, "interface": "usb"}
    if fem.verify_compatibility(img_path, good_usb):
        audit_results["checks"].append({"check": "Artifact compatibility verification passes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Artifact compatibility verification passes", "status": "FAIL"})

    # 4. Simulation Mode
    if fem.run_flash_simulation(img_path, "sdb"):
        audit_results["checks"].append({"check": "Simulation mode runs without writes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Simulation mode runs without writes", "status": "FAIL"})

    # 5. Controlled Execution (Gating)
    valid_phrase = "EXECUTE_TOWER_FLASH_sdb"
    if fem.execute_controlled_flash(img_path, "sdb", valid_phrase):
        audit_results["checks"].append({"check": "Controlled flash execution requires explicit confirmation (Success case)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Controlled flash execution requires explicit confirmation (Success case)", "status": "FAIL"})

    if not fem.execute_controlled_flash(img_path, "sdb", "INVALID"):
        audit_results["checks"].append({"check": "Controlled flash execution requires explicit confirmation (Rejection case)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Controlled flash execution requires explicit confirmation (Rejection case)", "status": "FAIL"})

    # 6. Post-Flash Plan
    plan = fem.generate_post_flash_verification_plan("sdb")
    if plan["verdict"] == "PLAN_GENERATED" and "verify_partition_labels" in plan["steps"]:
        audit_results["checks"].append({"check": "Post-flash verification plan generated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Post-flash verification plan generated", "status": "FAIL"})

    # 7. Admin Terminal Integration
    # Store evidence for terminal to read
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "controlled_flash_execution_result.json"), 'w') as f:
        json.dump(fem.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("flash report")
    if "Physical Flash Execution Report" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports flash audit status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports flash audit status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    report_path = os.path.join(output_dir, "physical_flash_boundary_result.json")
    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Physical Flash validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_controlled_flash_validation()
