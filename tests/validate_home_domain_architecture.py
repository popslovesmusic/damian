import os
import json
import jsonschema

def run_home_domain_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-009",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/domain/registry/home_domain_registry.json")
    state_schema_path = os.path.join(project_root, "engine/domain/contracts/domain_state.schema.json")
    action_schema_path = os.path.join(project_root, "engine/domain/contracts/domain_dashboard_action.schema.json")
    example_state_path = os.path.join(project_root, "engine/domain/contracts/example_domain_state.json")

    registry_data = {}
    state_schema_data = {}
    action_schema_data = {}
    example_state_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "home_domain_registry.json")
    state_schema_data = load_json_file(state_schema_path, "domain_state.schema.json")
    action_schema_data = load_json_file(action_schema_path, "domain_dashboard_action.schema.json")
    example_state_data = load_json_file(example_state_path, "example_domain_state.json")

    if not all([registry_data, state_schema_data, action_schema_data, example_state_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(state_schema_path)}/",
        referrer=state_schema_data
    )

    # Check 1: Home domain registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Home domain registry exists", "status": "PASS"})

    # Check 2: At least 3 domain archetypes are declared
    archetypes_count_check = {"check": "At least 3 domain archetypes are declared", "status": "PASS"}
    if not registry_data or "domain_archetypes" not in registry_data or len(registry_data["domain_archetypes"]) < 3:
        archetypes_count_check["status"] = "FAIL"
        archetypes_count_check["reason"] = "Registry missing or has less than 3 domain archetypes."
    audit_results["checks"].append(archetypes_count_check)

    # Check 3: Global rules include all_advantages_require_equal_or_greater_risk
    advantages_risk_check = {"check": "Global rules include all_advantages_require_equal_or_greater_risk", "status": "PASS"}
    if "global_rules" not in registry_data or "all_advantages_require_equal_or_greater_risk" not in registry_data["global_rules"]:
        advantages_risk_check["status"] = "FAIL"
        advantages_risk_check["reason"] = "'all_advantages_require_equal_or_greater_risk' not found in global_rules."
    audit_results["checks"].append(advantages_risk_check)

    # Check 4: Global rules include domain_owner_not_immune_to_domain_effects
    owner_immunity_check = {"check": "Global rules include domain_owner_not_immune_to_domain_effects", "status": "PASS"}
    if "global_rules" not in registry_data or "domain_owner_not_immune_to_domain_effects" not in registry_data["global_rules"]:
        owner_immunity_check["status"] = "FAIL"
        owner_immunity_check["reason"] = "'domain_owner_not_immune_to_domain_effects' not found in global_rules."
    audit_results["checks"].append(owner_immunity_check)

    # Check 5: Domain state schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Domain state schema exists", "status": "PASS"})

    # Check 6: Dashboard action schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Dashboard action schema exists", "status": "PASS"})

    # Check 7: Example domain state validates against schema
    example_validation_check = {"check": "Example domain state validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_state_data, schema=state_schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 8: Operational costs are present and non-negative
    operational_costs_check = {"check": "Operational costs are present and non-negative", "status": "PASS"}
    operational_costs = example_state_data.get("operational_costs")
    if not operational_costs:
        operational_costs_check["status"] = "FAIL"
        operational_costs_check["reason"] = "operational_costs not found in example_domain_state.json."
    else:
        for cost_name, cost_value in operational_costs.items():
            if not (isinstance(cost_value, (int, float)) and cost_value >= 0):
                operational_costs_check["status"] = "FAIL"
                operational_costs_check["reason"] = f"Operational cost '{cost_name}' is not non-negative: {cost_value}."
                break
    audit_results["checks"].append(operational_costs_check)

    # Check 9: Forbidden flags in example are all false
    forbidden_flags_check = {"check": "Forbidden flags in example are all false", "status": "PASS"}
    if "forbidden_flags" in example_state_data:
        for flag, value in example_state_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_domain_state.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_domain_state.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Check 10: Dashboard actions require both advantage_gained and risk_incurred (conceptual check, verified by schema structure)
    dashboard_action_contract_check = {"check": "Dashboard actions require both advantage_gained and risk_incurred", "status": "PASS"}
    if not (("advantage_gained" in action_schema_data.get("required", [])) and ("risk_incurred" in action_schema_data.get("required", []))):
        dashboard_action_contract_check["status"] = "FAIL"
        dashboard_action_contract_check["reason"] = "Dashboard action schema does not require both 'advantage_gained' and 'risk_incurred'."
    audit_results["checks"].append(dashboard_action_contract_check)
    

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_009_domain_conquest_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_009_domain_conquest_result.json")

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
    audit = run_home_domain_audit()
    print(json.dumps(audit, indent=2))
