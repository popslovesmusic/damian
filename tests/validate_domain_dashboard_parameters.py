import os
import json
import jsonschema

def run_domain_dashboard_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-013",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/domain/dashboard/domain_dashboard_parameter_registry.json")
    schema_path = os.path.join(project_root, "engine/domain/dashboard/contracts/domain_parameter_change.schema.json")
    example_change_path = os.path.join(project_root, "engine/domain/dashboard/contracts/example_domain_parameter_change.json")

    registry_data = {}
    schema_data = {}
    example_change_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "domain_dashboard_parameter_registry.json")
    schema_data = load_json_file(schema_path, "domain_parameter_change.schema.json")
    example_change_data = load_json_file(example_change_path, "example_domain_parameter_change.json")

    if not all([registry_data, schema_data, example_change_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Dashboard parameter registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Dashboard parameter registry exists", "status": "PASS"})

    # Check 2: Registry declares at least 6 parameters
    parameters_count_check = {"check": "Registry declares at least 6 parameters", "status": "PASS"}
    if not registry_data or "parameters" not in registry_data or len(registry_data["parameters"]) < 6:
        parameters_count_check["status"] = "FAIL"
        parameters_count_check["reason"] = "Registry missing or has less than 6 parameters."
    audit_results["checks"].append(parameters_count_check)

    # Check 3: Every parameter declares benefit and non-empty required_risks
    parameter_fields_check = {"check": "Every parameter declares benefit and non-empty required_risks", "status": "PASS"}
    if "parameters" in registry_data:
        for i, param in enumerate(registry_data["parameters"]):
            if not all(k in param for k in ["parameter_id", "benefit", "required_risks"]):
                parameter_fields_check["status"] = "FAIL"
                parameter_fields_check["reason"] = f"Parameter {i} missing required fields."
                break
            if not isinstance(param["required_risks"], list) or not param["required_risks"]:
                parameter_fields_check["status"] = "FAIL"
                parameter_fields_check["reason"] = f"Parameter {i} has empty or non-list required_risks."
                break
    else:
        parameter_fields_check["status"] = "FAIL"
        parameter_fields_check["reason"] = "Registry data missing 'parameters' key."
    audit_results["checks"].append(parameter_fields_check)

    # Check 4: Forbidden dashboard results include free_advantage
    free_advantage_check = {"check": "Forbidden dashboard results include free_advantage", "status": "PASS"}
    if "forbidden_dashboard_results" not in registry_data or "free_advantage" not in registry_data["forbidden_dashboard_results"]:
        free_advantage_check["status"] = "FAIL"
        free_advantage_check["reason"] = "'free_advantage' not found in forbidden_dashboard_results."
    audit_results["checks"].append(free_advantage_check)

    # Check 5: Forbidden dashboard results include positive_only_upgrade
    positive_only_upgrade_check = {"check": "Forbidden dashboard results include positive_only_upgrade", "status": "PASS"}
    if "forbidden_dashboard_results" not in registry_data or "positive_only_upgrade" not in registry_data["forbidden_dashboard_results"]:
        positive_only_upgrade_check["status"] = "FAIL"
        positive_only_upgrade_check["reason"] = "'positive_only_upgrade' not found in forbidden_dashboard_results."
    audit_results["checks"].append(positive_only_upgrade_check)

    # Check 6: Domain parameter change schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Domain parameter change schema exists", "status": "PASS"})

    # Check 7: Example parameter change validates against schema
    example_validation_check = {"check": "Example parameter change validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_change_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 8: Example owner_affected = true
    owner_affected_check = {"check": "Example owner_affected = true", "status": "PASS"}
    if example_change_data.get("owner_affected") is not True:
        owner_affected_check["status"] = "FAIL"
        owner_affected_check["reason"] = "'owner_affected' is not true in example_domain_parameter_change.json."
    audit_results["checks"].append(owner_affected_check)

    # Check 9: Example playability_preserved = true
    playability_preserved_check = {"check": "Example playability_preserved = true", "status": "PASS"}
    if example_change_data.get("playability_preserved") is not True:
        playability_preserved_check["status"] = "FAIL"
        playability_preserved_check["reason"] = "'playability_preserved' is not true in example_domain_parameter_change.json."
    audit_results["checks"].append(playability_preserved_check)

    # Check 10: Example primary_route_preserved = true
    primary_route_preserved_check = {"check": "Example primary_route_preserved = true", "status": "PASS"}
    if example_change_data.get("primary_route_preserved") is not True:
        primary_route_preserved_check["status"] = "FAIL"
        primary_route_preserved_check["reason"] = "'primary_route_preserved' is not true in example_domain_parameter_change.json."
    audit_results["checks"].append(primary_route_preserved_check)

    # Check 11: Example risk_advantage_equilibrium_preserved = true
    risk_advantage_equilibrium_preserved_check = {"check": "Example risk_advantage_equilibrium_preserved = true", "status": "PASS"}
    if example_change_data.get("risk_advantage_equilibrium_preserved") is not True:
        risk_advantage_equilibrium_preserved_check["status"] = "FAIL"
        risk_advantage_equilibrium_preserved_check["reason"] = "'risk_advantage_equilibrium_preserved' is not true in example_domain_parameter_change.json."
    audit_results["checks"].append(risk_advantage_equilibrium_preserved_check)

    # Check 12: Example forbidden flags are all false
    forbidden_flags_check = {"check": "Example forbidden flags are all false", "status": "PASS"}
    if "forbidden_flags" in example_change_data:
        for flag, value in example_change_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_domain_parameter_change.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_domain_parameter_change.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_013_domain_dashboard_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_013_domain_dashboard_result.json")

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
    audit = run_domain_dashboard_audit()
    print(json.dumps(audit, indent=2))
