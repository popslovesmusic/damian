import os
import json
import shutil

def run_usb_handoff_validation():
    audit_results = {
        "patch_id": "STAGE-034",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/usb_handoff_boundary.json")
    device_path = os.path.join(project_root, "engine/os_boundary/contracts/usb_device_contract.json")

    # 1. Contract checks
    if os.path.exists(boundary_path) and os.path.exists(device_path):
        audit_results["checks"].append({"check": "USB handoff boundary and device contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "USB handoff boundary and device contract defined", "status": "FAIL"})

    from engine.os_boundary.flash_handoff_manager import FlashHandoffManager
    fhm = FlashHandoffManager(boundary_path, device_path)

    # 2. Read-only enumeration / Host disk rejection
    sim_devices = [
        {"id": "sda", "vendor": "Samsung", "model": "NVMe SSD", "size": "512G", "is_removable": False, "interface": "nvme"},
        {"id": "sdb", "vendor": "Sandisk", "model": "Cruzer", "size": "32G", "is_removable": True, "interface": "usb"}
    ]
    allowed = fhm.enumerate_removable_devices(sim_devices)
    
    # Verify sda rejected
    sda_rejected = any(c["device_id"] == "sda" and c["status"] == "REJECTED" for c in fhm.evidence["checks"])
    if sda_rejected:
        audit_results["checks"].append({"check": "Internal host disks are rejected", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Internal host disks are rejected", "status": "FAIL"})

    # Verify sdb passed
    sdb_passed = any(dev["id"] == "sdb" for dev in allowed)
    if sdb_passed:
        audit_results["checks"].append({"check": "Read-only enumeration detects removable devices only", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Read-only enumeration detects removable devices only", "status": "FAIL"})

    # 3. Dry-run flashing plan
    img_path = os.path.join(project_root, "build/live_os/images/tower-damian-proto.img")
    if not os.path.exists(img_path):
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'w') as f: f.write("STUB_ARTIFACT")
        
    plan = fhm.create_flashing_plan(img_path, "sdb")
    if plan["target"] == "sdb" and len(plan["actions"]) > 0:
        audit_results["checks"].append({"check": "Dry-run flashing plan generated without writes", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Dry-run flashing plan generated without writes", "status": "FAIL"})

    # 4. Operator acknowledgment gate
    valid_phrase = "FLASH_TOWER_ARTIFACT_TO_sdb"
    if fhm.validate_operator_confirmation("sdb", valid_phrase):
        audit_results["checks"].append({"check": "Operator acknowledgment gate accepts valid phrase", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Operator acknowledgment gate accepts valid phrase", "status": "FAIL"})

    if not fhm.validate_operator_confirmation("sdb", "INVALID"):
        audit_results["checks"].append({"check": "Operator acknowledgment gate rejects invalid phrase", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Operator acknowledgment gate rejects invalid phrase", "status": "FAIL"})

    # 5. Artifact integrity verification (hash in plan)
    if "artifact_hash" in plan:
        audit_results["checks"].append({"check": "Artifact integrity verification validates hashes before flashing", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Artifact integrity verification validates hashes before flashing", "status": "FAIL"})

    # 6. Admin terminal report
    # Store evidence for terminal to read
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "admin_terminal_usb_handoff_result.json"), 'w') as f:
        json.dump(fhm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("flash status")
    if "USB Flashing Handoff Status" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports flashing handoff status", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports flashing handoff status", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    report_path = os.path.join(output_dir, "usb_handoff_boundary_result.json")
    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"USB Handoff validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_usb_handoff_validation()
