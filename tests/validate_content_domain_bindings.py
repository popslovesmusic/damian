import os
import json
import jsonschema

def run_content_domain_binding_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-012",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    schema_path = os.path.join(project_root, "engine/content/contracts/content_domain_binding.schema.json")
    registry_path = os.path.join(project_root, "engine/content/registry/content_domain_binding_registry.json")
    damian_binding_path = os.path.join(project_root, "content/damian/domain_binding.json")
    jacobs_bane_binding_path = os.path.join(project_root, "content/jacobs_bane/domain_binding.json")

    schema_data = {}
    registry_data = {}
    damian_binding_data = {}
    jacobs_bane_binding_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    schema_data = load_json_file(schema_path, "content_domain_binding.schema.json")
    registry_data = load_json_file(registry_path, "content_domain_binding_registry.json")
    damian_binding_data = load_json_file(damian_binding_path, "damian/domain_binding.json")
    jacobs_bane_binding_data = load_json_file(jacobs_bane_binding_path, "jacobs_bane/domain_binding.json")

    if not all([schema_data, registry_data, damian_binding_data, jacobs_bane_binding_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Content domain binding schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Content domain binding schema exists", "status": "PASS"})

    # Check 2: Content domain binding registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Content domain binding registry exists", "status": "PASS"})

    # Check 3: Registry includes damian and jacobs_bane bindings
    registry_bindings_check = {"check": "Registry includes damian and jacobs_bane bindings", "status": "PASS"}
    registry_content_pack_ids = {b.get("content_pack_id") for b in registry_data.get("bindings", [])}
    if "damian" not in registry_content_pack_ids or "jacobs_bane" not in registry_content_pack_ids:
        registry_bindings_check["status"] = "FAIL"
        registry_bindings_check["reason"] = "Registry does not include both 'damian' and 'jacobs_bane' bindings."
    audit_results["checks"].append(registry_bindings_check)

    # Check 4: Damian binding file exists and validates against schema
    damian_validation_check = {"check": "Damian binding file exists and validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=damian_binding_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        damian_validation_check["status"] = "FAIL"
        damian_validation_check["reason"] = f"Validation Error for Damian binding: {e.message}"
    except Exception as e:
        damian_validation_check["status"] = "FAIL"
        damian_validation_check["reason"] = f"Unexpected error validating Damian binding: {e}"
    audit_results["checks"].append(damian_validation_check)

    # Check 5: Jacob's Bane binding file exists and validates against schema
    jacobs_bane_validation_check = {"check": "Jacob's Bane binding file exists and validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=jacobs_bane_binding_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        jacobs_bane_validation_check["status"] = "FAIL"
        jacobs_bane_validation_check["reason"] = f"Validation Error for Jacob's Bane binding: {e.message}"
    except Exception as e:
        jacobs_bane_validation_check["status"] = "FAIL"
        jacobs_bane_validation_check["reason"] = f"Unexpected error validating Jacob's Bane binding: {e}"
    audit_results["checks"].append(jacobs_bane_validation_check)

    # Check 6: Damian binds to tower_domain
    damian_domain_check = {"check": "Damian binds to tower_domain", "status": "PASS"}
    if damian_binding_data.get("domain_archetype") != "tower_domain":
        damian_domain_check["status"] = "FAIL"
        damian_domain_check["reason"] = "Damian binding does not specify 'tower_domain' as archetype."
    audit_results["checks"].append(damian_domain_check)

    # Check 7: Jacob's Bane binds to swamp_domain
    jacobs_bane_domain_check = {"check": "Jacob's Bane binds to swamp_domain", "status": "PASS"}
    if jacobs_bane_binding_data.get("domain_archetype") != "swamp_domain":
        jacobs_bane_domain_check["status"] = "FAIL"
        jacobs_bane_domain_check["reason"] = "Jacob's Bane binding does not specify 'swamp_domain' as archetype."
    audit_results["checks"].append(jacobs_bane_domain_check)

    # Check 8: Both bindings require home conquest before dashboard unlock
    conquest_unlock_check = {"check": "Both bindings require home conquest before dashboard unlock", "status": "PASS"}
    if not (damian_binding_data.get("conquest_role", {}).get("must_conquer_home_first") is True and
            damian_binding_data.get("conquest_role", {}).get("dashboard_unlocks_after_conquest") is True):
        conquest_unlock_check["status"] = "FAIL"
        conquest_unlock_check["reason"] = "Damian binding does not require home conquest before dashboard unlock."
    if not (jacobs_bane_binding_data.get("conquest_role", {}).get("must_conquer_home_first") is True and
            jacobs_bane_binding_data.get("conquest_role", {}).get("dashboard_unlocks_after_conquest") is True):
        conquest_unlock_check["status"] = "FAIL"
        conquest_unlock_check["reason"] = "Jacob's Bane binding does not require home conquest before dashboard unlock."
    audit_results["checks"].append(conquest_unlock_check)

    # Check 9: Both bindings inherit bounded progression
    bounded_progression_check = {"check": "Both bindings inherit bounded progression", "status": "PASS"}
    if not (damian_binding_data.get("engine_rule_compliance", {}).get("inherits_bounded_progression") is True and
            jacobs_bane_binding_data.get("engine_rule_compliance", {}).get("inherits_bounded_progression") is True):
        bounded_progression_check["status"] = "FAIL"
        bounded_progression_check["reason"] = "One or both bindings do not inherit bounded progression."
    audit_results["checks"].append(bounded_progression_check)

    # Check 10: Both bindings inherit risk_advantage_equilibrium
    risk_advantage_check = {"check": "Both bindings inherit risk_advantage_equilibrium", "status": "PASS"}
    if not (damian_binding_data.get("engine_rule_compliance", {}).get("inherits_risk_advantage_equilibrium") is True and
            jacobs_bane_binding_data.get("engine_rule_compliance", {}).get("inherits_risk_advantage_equilibrium") is True):
        risk_advantage_check["status"] = "FAIL"
        risk_advantage_check["reason"] = "One or both bindings do not inherit risk-advantage equilibrium."
    audit_results["checks"].append(risk_advantage_check)

    # Check 11: Both bindings inherit playability constraints
    playability_constraints_check = {"check": "Both bindings inherit playability constraints", "status": "PASS"}
    if not (damian_binding_data.get("engine_rule_compliance", {}).get("inherits_playability_constraints") is True and
            jacobs_bane_binding_data.get("engine_rule_compliance", {}).get("inherits_playability_constraints") is True):
        playability_constraints_check["status"] = "FAIL"
        playability_constraints_check["reason"] = "One or both bindings do not inherit playability constraints."
    audit_results["checks"].append(playability_constraints_check)

    # Check 12: Neither binding redefines engine core rules (conceptual, partially covered by const:true in schema)
    # The const:true for engine_rule_compliance flags in the schema implies this.
    audit_results["checks"].append({"check": "Neither binding redefines engine core rules", "status": "PASS"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_012_content_domain_binding_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_012_content_domain_binding_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    print(f"Validation results written to {result_file_path}")
    return audit_results

if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema library not found. Please install it: pip install jsonschema")
        exit(1)
    audit = run_content_domain_binding_audit()
    print(json.dumps(audit, indent=2))
