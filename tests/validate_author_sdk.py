import os
import json
import shutil
import subprocess

def run_author_sdk_validation():
    audit_results = {
        "patch_id": "STAGE-053",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/sdk/contracts/sdk_boundary.json")
    contract_path = os.path.join(project_root, "engine/sdk/contracts/expansion_contract_schema.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "SDK boundary and expansion contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "SDK boundary and expansion contract defined", "status": "FAIL"})

    from engine.sdk.runtime.sdk_manager import SdkManager
    sm = SdkManager(boundary_path, contract_path)

    # 2. Validation Pipeline (Pass Case)
    valid_manifest = {
        "expansion_id": "ext_lore_test",
        "author_id": "author_test",
        "world_context": "damian_core",
        "supported_engine_version": "0.1.0",
        "narrative_modules": ["flavor.json"],
        "contract_modules": [],
        "market_modules": [],
        "faction_modules": [],
        "relay_interaction_profile": "read_only",
        "sandbox_permissions": ["story_modules"],
        "bounded_flags": {"safe": True},
        "expansion_hash": "hash_123"
    }
    if sm.validate_cartridge(valid_manifest):
        audit_results["checks"].append({"check": "Validation pipeline accepts safe cartridge", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Validation pipeline accepts safe cartridge", "status": "FAIL"})

    # 3. Validation Pipeline (Fail Cases)
    invalid_domain = valid_manifest.copy()
    invalid_domain["sandbox_permissions"] = ["os_execution"]
    if not sm.validate_cartridge(invalid_domain):
        audit_results["checks"].append({"check": "Validation pipeline rejects unsafe domain", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Validation pipeline rejects unsafe domain", "status": "FAIL"})

    invalid_payload = valid_manifest.copy()
    invalid_payload["narrative_modules"] = ["script.sh"]
    if not sm.validate_cartridge(invalid_payload):
        audit_results["checks"].append({"check": "Validation pipeline rejects unsafe payload", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Validation pipeline rejects unsafe payload", "status": "FAIL"})

    # 4. API Bounding
    narrative_res = sm.stub_narrative_sdk("Test text")
    if "[AUTHOR_EXTENSION]" in narrative_res:
        audit_results["checks"].append({"check": "Narrative SDK preserves tower identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Narrative SDK preserves tower identity", "status": "FAIL"})

    contract_res = sm.stub_author_contract("Test quest", 1000)
    if contract_res["reward_value"] <= 100:
        audit_results["checks"].append({"check": "Author contract generation bounded", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Author contract generation bounded", "status": "FAIL"})

    # 5. Publishing Pipeline
    package = sm.publish_expansion(valid_manifest)
    if "published_id" in package and package["status"] == "PUBLISHED_TO_RELAY":
        audit_results["checks"].append({"check": "Publishing pipeline preserves lineage", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Publishing pipeline preserves lineage", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "cartridge_validation_pipeline_result.json"), 'w') as f:
        json.dump(sm.get_final_evidence(), f, indent=2)
    with open(os.path.join(output_dir, "expansion_publishing_result.json"), 'w') as f:
        json.dump(package, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("sdk validate")
    if "Expansion Validation Pipeline Status" in res and "verdict" in res:
        audit_results["checks"].append({"check": "Admin terminal reports sdk state safely", "status": "PASS"})
    else:
        # Debug why it's failing
        print(f"Terminal Output: {res}")
        audit_results["checks"].append({"check": "Admin terminal reports sdk state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_053_author_sdk_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Author SDK validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_author_sdk_validation()
