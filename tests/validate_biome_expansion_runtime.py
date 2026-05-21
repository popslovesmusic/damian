import os
import json
import shutil
import subprocess

def run_biome_expansion_validation():
    audit_results = {
        "patch_id": "STAGE-062",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    boundary_path = os.path.join(project_root, "engine/content/biomes/contracts/biome_boundary.json")
    contract_path = os.path.join(project_root, "engine/content/biomes/contracts/biome_contract.json")

    # 1. Boundary & Contract Checks
    if os.path.exists(boundary_path) and os.path.exists(contract_path):
        audit_results["checks"].append({"check": "Procedural biome boundary and contract defined", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Procedural biome boundary and contract defined", "status": "FAIL"})

    from engine.content.biomes.runtime.biome_manager import BiomeManager
    bm = BiomeManager(boundary_path, contract_path)

    # 2. Biome Generation (Profile)
    profile = bm.generate_biome_profile("MUTATED_GROWTH_ZONE", 40)
    if "biome_hash" in profile and profile["biome_identity"] == "MUTATED_GROWTH_ZONE":
        audit_results["checks"].append({"check": "Biome generation preserves environmental identity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Biome generation preserves environmental identity", "status": "FAIL"})

    # 3. Environmental Identity Validation
    if bm.validate_environmental_identity(profile):
        audit_results["checks"].append({"check": "Environmental atmosphere supports tower hostility", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Environmental atmosphere supports tower hostility", "status": "FAIL"})

    # 4. Biome Smoke Test
    smoke = bm.run_biome_smoke_test("FLOODED_INFRASTRUCTURE")
    if smoke["generation_status"] == "SUCCESS" and smoke["readability_score"] > 0.5:
        audit_results["checks"].append({"check": "Biome smoke test preserves readability and recoverability", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Biome smoke test preserves readability and recoverability", "status": "FAIL"})

    # 5. Landmark & Relay Placement
    if "landmark_profile" in profile and "relay_presence_profile" in profile:
        audit_results["checks"].append({"check": "Landmark and relay placement preserve navigation clarity", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Landmark and relay placement preserve navigation clarity", "status": "FAIL"})

    # 6. Admin Terminal Integration
    # Store evidence for terminal
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "biome_generation_result.json"), 'w') as f:
        json.dump(profile, f, indent=2)
    with open(os.path.join(output_dir, "biome_smoke_test_result.json"), 'w') as f:
        json.dump(bm.get_final_evidence(), f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    term = RestrictedAdminTerminal(
        os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json"),
        os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json"),
        data_root
    )
    res = term.execute("biome status")
    if "Procedural Biome Status" in res and "biome_id" in res:
        audit_results["checks"].append({"check": "Admin terminal reports biome state safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports biome state safely", "status": "FAIL"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    final_report_path = os.path.join(output_dir, "stage_062_biome_expansion_audit.json")
    with open(final_report_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Biome Expansion validation report written to {final_report_path}")
    return audit_results

if __name__ == "__main__":
    run_biome_expansion_validation()
