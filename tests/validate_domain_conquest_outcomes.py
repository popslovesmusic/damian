import os
import json
import jsonschema

def run_domain_conquest_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-014",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/domain/conquest/domain_conquest_outcome_registry.json")
    schema_path = os.path.join(project_root, "engine/domain/conquest/contracts/domain_conquest_resolution.schema.json")
    example_resolution_path = os.path.join(project_root, "engine/domain/conquest/contracts/example_domain_conquest_resolution.json")

    registry_data = {}
    schema_data = {}
    example_resolution_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "domain_conquest_outcome_registry.json")
    schema_data = load_json_file(schema_path, "domain_conquest_resolution.schema.json")
    example_resolution_data = load_json_file(example_resolution_path, "example_domain_conquest_resolution.json")

    if not all([registry_data, schema_data, example_resolution_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Domain conquest outcome registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Domain conquest outcome registry exists", "status": "PASS"})

    # Check 2: Registry declares at least 6 outcome modes
    outcome_modes_count_check = {"check": "Registry declares at least 6 outcome modes", "status": "PASS"}
    if not registry_data or "outcome_modes" not in registry_data or len(registry_data["outcome_modes"]) < 6:
        outcome_modes_count_check["status"] = "FAIL"
        outcome_modes_count_check["reason"] = "Registry missing or has less than 6 outcome modes."
    audit_results["checks"].append(outcome_modes_count_check)

    # Check 3: Outcome modes include ATTACKER_CONQUEST, DEFENDER_HOLD, SESSION_UNRESOLVED, and FAILED_SAFE
    required_outcomes_check = {"check": "Outcome modes include ATTACKER_CONQUEST, DEFENDER_HOLD, SESSION_UNRESOLVED, and FAILED_SAFE", "status": "PASS"}
    required_outcomes = {"ATTACKER_CONQUEST", "DEFENDER_HOLD", "SESSION_UNRESOLVED", "FAILED_SAFE"}
    current_outcomes = {om.get("outcome_id") for om in registry_data.get("outcome_modes", [])}
    if not required_outcomes.issubset(current_outcomes):
        required_outcomes_check["status"] = "FAIL"
        required_outcomes_check["reason"] = f"Missing required outcomes: {required_outcomes - current_outcomes}."
    audit_results["checks"].append(required_outcomes_check)

    # Check 4: Global rules include conquest_grants_influence_not_permanent_theft
    conquest_theft_check = {"check": "Global rules include conquest_grants_influence_not_permanent_theft", "status": "PASS"}
    if "global_rules" not in registry_data or "conquest_grants_influence_not_permanent_theft" not in registry_data["global_rules"]:
        conquest_theft_check["status"] = "FAIL"
        conquest_theft_check["reason"] = "'conquest_grants_influence_not_permanent_theft' not found in global_rules."
    audit_results["checks"].append(conquest_theft_check)

    # Check 5: Global rules include owner_domain_must_remain_recoverable
    domain_recoverable_check = {"check": "Global rules include owner_domain_must_remain_recoverable", "status": "PASS"}
    if "global_rules" not in registry_data or "owner_domain_must_remain_recoverable" not in registry_data["global_rules"]:
        domain_recoverable_check["status"] = "FAIL"
        domain_recoverable_check["reason"] = "'owner_domain_must_remain_recoverable' not found in global_rules."
    audit_results["checks"].append(domain_recoverable_check)

    # Check 6: Resolution schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Resolution schema exists", "status": "PASS"})

    # Check 7: Example resolution validates against schema
    example_validation_check = {"check": "Example resolution validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_resolution_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 8: Example writes residue to attacker, defender, and domain
    residue_written_check = {"check": "Example writes residue to attacker, defender, and domain", "status": "PASS"}
    if not (example_resolution_data.get("residue_results", {}).get("attacker_residue_written") is True and
            example_resolution_data.get("residue_results", {}).get("defender_residue_written") is True and
            example_resolution_data.get("residue_results", {}).get("domain_residue_written") is True):
        residue_written_check["status"] = "FAIL"
        residue_written_check["reason"] = "Residue not written to attacker, defender, and domain in example."
    audit_results["checks"].append(residue_written_check)

    # Check 9: Example preserves playability and primary route
    playability_preserved_check = {"check": "Example preserves playability and primary route", "status": "PASS"}
    if not (example_resolution_data.get("playability_results", {}).get("playability_preserved") is True and
            example_resolution_data.get("playability_results", {}).get("primary_route_preserved") is True):
        playability_preserved_check["status"] = "FAIL"
        playability_preserved_check["reason"] = "Playability or primary route not preserved in example."
    audit_results["checks"].append(playability_preserved_check)

    # Check 10: Example domain_remains_owner_recoverable = true
    owner_recoverable_check = {"check": "Example domain_remains_owner_recoverable = true", "status": "PASS"}
    if example_resolution_data.get("domain_effects", {}).get("domain_remains_owner_recoverable") is not True:
        owner_recoverable_check["status"] = "FAIL"
        owner_recoverable_check["reason"] = "'domain_remains_owner_recoverable' is not true in example."
    audit_results["checks"].append(owner_recoverable_check)


    # Check 11: Example forbidden flags are all false
    forbidden_flags_check = {"check": "Example forbidden flags are all false", "status": "PASS"}
    if "forbidden_flags" in example_resolution_data:
        for flag, value in example_resolution_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_domain_conquest_resolution.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_domain_conquest_resolution.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_014_domain_conquest_outcome_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_014_domain_conquest_outcome_result.json")

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
    audit = run_domain_conquest_audit()
    print(json.dumps(audit, indent=2))
