import os
import json
import shutil
import subprocess

def run_content_pack_validation():
    audit_results = {
        "patch_id": "STAGE-032",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/content_pack_cartridge_boundary.json")
    manifest_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/content_pack_manifest_contract.json")

    # 1. Check Boundary & Contract
    if os.path.exists(boundary_path) and os.path.exists(manifest_contract_path):
        audit_results["checks"].append({"check": "Content pack boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Content pack boundary and contract defined", "status": "FAIL"})

    from engine.os_boundary.cartridge_verifier import CartridgeVerifier
    verifier = CartridgeVerifier(boundary_path, manifest_contract_path)

    # 2. Validate Damian Content Pack
    damian_dir = os.path.join(project_root, "content/damian")
    damian_manifest_path = os.path.join(damian_dir, "cartridge_manifest.json")
    
    if os.path.exists(damian_manifest_path):
        with open(damian_manifest_path, 'r') as f:
            damian_manifest = json.load(f)
        
        v1 = verifier.verify_manifest_schema(damian_manifest)
        v2 = verifier.safety_scan(damian_manifest)
        v3 = verifier.verify_hashes(damian_dir, damian_manifest)
        
        if v1 and v2 and v3:
            audit_results["checks"].append({"check": "Damian default content pack validates", "status": "PASS"})
        else:
            audit_results["checks"].append({"check": "Damian default content pack validates", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Damian manifest exists", "status": "FAIL"})

    # 3. Validate Jacob's Bane Content Pack
    jb_dir = os.path.join(project_root, "content/jacobs_bane")
    jb_manifest_path = os.path.join(jb_dir, "cartridge_manifest.json")
    
    if os.path.exists(jb_manifest_path):
        with open(jb_manifest_path, 'r') as f:
            jb_manifest = json.load(f)
        
        v1 = verifier.verify_manifest_schema(jb_manifest)
        v2 = verifier.safety_scan(jb_manifest)
        v3 = verifier.verify_hashes(jb_dir, jb_manifest)
        
        if v1 and v2 and v3:
            audit_results["checks"].append({"check": "Jacob's Bane content pack validates", "status": "PASS"})
        else:
            audit_results["checks"].append({"check": "Jacob's Bane content pack validates", "status": "FAIL"})
    else:
        audit_results["checks"].append({"check": "Jacob's Bane manifest exists", "status": "FAIL"})

    # 4. Check Hash Verification (Negative case: Modified Pack)
    if os.path.exists(damian_manifest_path):
        # Create a modified pack stub
        test_dir = os.path.join(project_root, "build/modified_pack_test")
        os.makedirs(test_dir, exist_ok=True)
        shutil.copy2(damian_manifest_path, os.path.join(test_dir, "cartridge_manifest.json"))
        # Create one file with wrong hash
        with open(os.path.join(test_dir, "content_pack.json"), 'w') as f:
            f.write("MODIFIED CONTENT")
            
        if not verifier.verify_hashes(test_dir, damian_manifest):
            audit_results["checks"].append({"check": "Hash verification rejects modified pack", "status": "PASS"})
        else:
            audit_results["checks"].append({"check": "Hash verification rejects modified pack", "status": "FAIL"})
    
    # 5. Check Safety Scanner (Negative case: Path Traversal)
    unsafe_manifest = damian_manifest.copy()
    unsafe_manifest["declared_files"] = ["../../etc/shadow"]
    if not verifier.safety_scan(unsafe_manifest):
        audit_results["checks"].append({"check": "Safety scanner rejects path traversal", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Safety scanner rejects path traversal", "status": "FAIL"})

    # 6. Check Safety Scanner (Negative case: Executable Payload)
    unsafe_manifest["declared_files"] = ["script.sh"]
    if not verifier.safety_scan(unsafe_manifest):
        audit_results["checks"].append({"check": "Safety scanner rejects executable payload declarations", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Safety scanner rejects executable payload declarations", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "content_pack_cartridge_verification_result.json")

    with open(report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Content pack validation report written to {report_path}")
    return audit_results

if __name__ == "__main__":
    run_content_pack_validation()
