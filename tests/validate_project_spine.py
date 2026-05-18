import os
import json

def run_spine_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-001",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Validation requirements
    required_files = [
        "engine/core/engine_manifest.json",
        "engine/core/system_registry.json",
        "content/damian/content_pack.json",
        "content/jacobs_bane/content_pack.json"
    ]

    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        check_name = f"{file_path} exists"
        if os.path.exists(full_path):
            audit_results["checks"].append({"check": check_name, "status": "PASS"})
        else:
            audit_results["checks"].append({"check": check_name, "status": "FAIL"})

    # Check for Damian not hardcoded as engine identity
    damian_as_engine_identity_check = {
        "check": "Damian appears only as content pack identity, not engine identity",
        "status": "PASS"
    }
    try:
        with open(os.path.join(project_root, "engine/core/engine_manifest.json"), 'r') as f:
            engine_manifest = json.load(f)
            if "Damian" in engine_manifest.get("engine_name", ""):
                damian_as_engine_identity_check["status"] = "FAIL"
                damian_as_engine_identity_check["reason"] = "Damian found in engine_name"
            elif "Damian" in str(engine_manifest.get("core_systems", [])):
                damian_as_engine_identity_check["status"] = "FAIL"
                damian_as_engine_identity_check["reason"] = "Damian found in core_systems"
    except Exception as e:
        damian_as_engine_identity_check["status"] = "FAIL"
        damian_as_engine_identity_check["reason"] = f"Error reading engine_manifest.json: {e}"
    audit_results["checks"].append(damian_as_engine_identity_check)

    # Check for Jacob's Bane as second content pack placeholder
    jacobs_bane_placeholder_check = {
        "check": "Jacob's Bane appears as second content pack placeholder",
        "status": "PASS"
    }
    try:
        with open(os.path.join(project_root, "content/jacobs_bane/content_pack.json"), 'r') as f:
            jacobs_bane_pack = json.load(f)
            if jacobs_bane_pack.get("title") != "Jacob's Bane":
                jacobs_bane_placeholder_check["status"] = "FAIL"
                jacobs_bane_placeholder_check["reason"] = "Jacob's Bane content pack title mismatch"
            if not jacobs_bane_pack.get("campaign_role") == "placeholder_campaign":
                 jacobs_bane_placeholder_check["status"] = "FAIL"
                 jacobs_bane_placeholder_check["reason"] = "Jacob's Bane content pack campaign_role mismatch"
    except Exception as e:
        jacobs_bane_placeholder_check["status"] = "FAIL"
        jacobs_bane_placeholder_check["reason"] = f"Error reading content/jacobs_bane/content_pack.json: {e}"
    audit_results["checks"].append(jacobs_bane_placeholder_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_001_spine_audit.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_spine_audit()
    print(json.dumps(audit, indent=2))
