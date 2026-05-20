import json
import os
import hashlib

def run_bootable_image_validation():
    audit_results = {
        "patch_id": "STAGE-025",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 1. Check Boundary Contract
    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/bootable_image_boundary.json")
    if os.path.exists(boundary_path):
        audit_results["checks"].append({"check": "Bootable image boundary defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Bootable image boundary defined", "status": "FAIL"})

    # 2. Check Image Config
    config_path = os.path.join(project_root, "os/kiosk/image_config.json")
    if os.path.exists(config_path):
        audit_results["checks"].append({"check": "Image config schema exists", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Image config schema exists", "status": "FAIL"})

    # 3. Check Assembly Plan
    plan_path = os.path.join(project_root, "build/live_os/images/assembly_plan.json")
    if os.path.exists(plan_path):
        audit_results["checks"].append({"check": "Assembly plan generated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Assembly plan generated", "status": "FAIL"})

    # 4. Check Artifact Stub and Hash Manifest
    manifest_path = os.path.join(project_root, "build/live_os/images/tower_image_manifest.json")
    if os.path.exists(manifest_path):
        audit_results["checks"].append({"check": "Safe image artifact stub created", "status": "PASS"})
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        image_path = os.path.join(project_root, "build/live_os/images/", manifest["filename"])
        
        if os.path.exists(image_path):
            # Verify Hash
            sha256_hash = hashlib.sha256()
            with open(image_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            if sha256_hash.hexdigest() == manifest["hash_sha256"]:
                audit_results["checks"].append({"check": "Hash manifest validator passes", "status": "PASS"})
            else:
                audit_results["checks"].append({"check": "Hash manifest validator passes", "status": "FAIL", "reason": "Hash mismatch."})
        else:
             audit_results["checks"].append({"check": "Image file exists", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Safe image artifact stub created", "status": "FAIL"})

    # 5. Check Manual Handoff Doc
    handoff_doc = os.path.join(project_root, "docs/design/os/manual_usb_flashing_handoff.md")
    if os.path.exists(handoff_doc):
        audit_results["checks"].append({"check": "Manual USB handoff documented", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Manual USB handoff documented", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_image_hash_report.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Hash report written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    run_bootable_image_validation()
