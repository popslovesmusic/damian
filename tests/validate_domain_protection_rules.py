import os
import json
import jsonschema

def run_domain_protection_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-015",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/domain/protection/domain_protection_registry.json")
    schema_path = os.path.join(project_root, "engine/domain/protection/contracts/domain_protection_state.schema.json")
    example_state_path = os.path.join(project_root, "engine/domain/protection/contracts/example_domain_protection_state.json")

    registry_data = {}
    schema_data = {}
    example_state_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "domain_protection_registry.json")
    schema_data = load_json_file(schema_path, "domain_protection_state.schema.json")
    example_state_data = load_json_file(example_state_path, "example_domain_protection_state.json")

    if not all([registry_data, schema_data, example_state_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Domain protection registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Domain protection registry exists", "status": "PASS"})

    # Check 2: Registry declares at least 5 protection states
    protection_states_check = {"check": "Registry declares at least 5 protection states", "status": "PASS"}
    if not registry_data or "protection_states" not in registry_data or len(registry_data["protection_states"]) < 5:
        protection_states_check["status"] = "FAIL"
        protection_states_check["reason"] = "Registry missing or has less than 5 protection states."
    audit_results["checks"].append(protection_states_check)

    # Check 3: Protection states include RECOVERY_WINDOW, LOW_ACTIVITY_SHIELD, and FAILED_SAFE_LOCK
    required_states_check = {"check": "Protection states include RECOVERY_WINDOW, LOW_ACTIVITY_SHIELD, and FAILED_SAFE_LOCK", "status": "PASS"}
    required_states = {"RECOVERY_WINDOW", "LOW_ACTIVITY_SHIELD", "FAILED_SAFE_LOCK"}
    current_states = {s.get("state_id") for s in registry_data.get("protection_states", [])}
    if not required_states.issubset(current_states):
        required_states_check["status"] = "FAIL"
        required_states_check["reason"] = f"Missing required protection states: {required_states - current_states}."
    audit_results["checks"].append(required_states_check)

    # Check 4: Anti-griefing rules include same_attacker_repeat_invasions_require_escalating_cost
    anti_griefing_cost_check = {"check": "Anti-griefing rules include same_attacker_repeat_invasions_require_escalating_cost", "status": "PASS"}
    if "anti_griefing_rules" not in registry_data or "same_attacker_repeat_invasions_require_escalating_cost" not in registry_data["anti_griefing_rules"]:
        anti_griefing_cost_check["status"] = "FAIL"
        anti_griefing_cost_check["reason"] = "'same_attacker_repeat_invasions_require_escalating_cost' not found in anti_griefing_rules."
    audit_results["checks"].append(anti_griefing_cost_check)

    # Check 5: Anti-griefing rules include protection_windows_do_not_grant_permanent_immunity
    anti_griefing_immunity_check = {"check": "Anti-griefing rules include protection_windows_do_not_grant_permanent_immunity", "status": "PASS"}
    if "anti_griefing_rules" not in registry_data or "protection_windows_do_not_grant_permanent_immunity" not in registry_data["anti_griefing_rules"]:
        anti_griefing_immunity_check["status"] = "FAIL"
        anti_griefing_immunity_check["reason"] = "'protection_windows_do_not_grant_permanent_immunity' not found in anti_griefing_rules."
    audit_results["checks"].append(anti_griefing_immunity_check)

    # Check 6: Recovery rules include domain_residue_persists_after_recovery
    recovery_residue_check = {"check": "Recovery rules include domain_residue_persists_after_recovery", "status": "PASS"}
    if "recovery_rules" not in registry_data or "domain_residue_persists_after_recovery" not in registry_data["recovery_rules"]:
        recovery_residue_check["status"] = "FAIL"
        recovery_residue_check["reason"] = "'domain_residue_persists_after_recovery' not found in recovery_rules."
    audit_results["checks"].append(recovery_residue_check)

    # Check 7: Protection state schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Protection state schema exists", "status": "PASS"})

    # Check 8: Example protection state validates against schema
    example_validation_check = {"check": "Example protection state validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_state_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 9: Example domain_recoverable = true
    domain_recoverable_check_example = {"check": "Example domain_recoverable = true", "status": "PASS"}
    if example_state_data.get("domain_recoverable") is not True:
        domain_recoverable_check_example["status"] = "FAIL"
        domain_recoverable_check_example["reason"] = "'domain_recoverable' is not true in example_domain_protection_state.json."
    audit_results["checks"].append(domain_recoverable_check_example)

    # Check 10: Example permanent_immunity_granted = false
    permanent_immunity_granted_check_example = {"check": "Example permanent_immunity_granted = false", "status": "PASS"}
    if example_state_data.get("permanent_immunity_granted") is not False:
        permanent_immunity_granted_check_example["status"] = "FAIL"
        permanent_immunity_granted_check_example["reason"] = "'permanent_immunity_granted' is not false in example_domain_protection_state.json."
    audit_results["checks"].append(permanent_immunity_granted_check_example)

    # Check 11: Example protection_expires = true
    protection_expires_check_example = {"check": "Example protection_expires = true", "status": "PASS"}
    if example_state_data.get("protection_expires") is not True:
        protection_expires_check_example["status"] = "FAIL"
        protection_expires_check_example["reason"] = "'protection_expires' is not true in example_domain_protection_state.json."
    audit_results["checks"].append(protection_expires_check_example)

    # Check 12: Example requires escalating cost for repeat attack
    escalating_cost_check_example = {"check": "Example requires escalating cost for repeat attack", "status": "PASS"}
    if example_state_data.get("escalating_cost_required_for_repeat_attack") is not True:
        escalating_cost_check_example["status"] = "FAIL"
        escalating_cost_check_example["reason"] = "'escalating_cost_required_for_repeat_attack' is not true in example_domain_protection_state.json."
    audit_results["checks"].append(escalating_cost_check_example)

    # Check 13: Example forbidden flags are all false
    forbidden_flags_check = {"check": "Example forbidden flags are all false", "status": "PASS"}
    if "forbidden_flags" in example_state_data:
        for flag, value in example_state_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_domain_protection_state.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_domain_protection_state.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_015_domain_protection_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_015_domain_protection_result.json")

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
    audit = run_domain_protection_audit()
    print(json.dumps(audit, indent=2))
