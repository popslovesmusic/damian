import os
import json
import jsonschema

def run_operational_economy_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-010",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/economy/registry/economy_resource_registry.json")
    schema_path = os.path.join(project_root, "engine/economy/contracts/operational_cost_profile.schema.json")
    example_profile_path = os.path.join(project_root, "engine/economy/contracts/example_operational_cost_profile.json")

    registry_data = {}
    schema_data = {}
    example_profile_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "economy_resource_registry.json")
    schema_data = load_json_file(schema_path, "operational_cost_profile.schema.json")
    example_profile_data = load_json_file(example_profile_path, "example_operational_cost_profile.json")

    if not all([registry_data, schema_data, example_profile_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Economy resource registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Economy resource registry exists", "status": "PASS"})

    # Check 2: At least 5 resource classes are declared
    resource_classes_count_check = {"check": "At least 5 resource classes are declared", "status": "PASS"}
    if not registry_data or "resource_classes" not in registry_data or len(registry_data["resource_classes"]) < 5:
        resource_classes_count_check["status"] = "FAIL"
        resource_classes_count_check["reason"] = "Registry missing or has less than 5 resource classes."
    audit_results["checks"].append(resource_classes_count_check)

    # Check 3: Global rules include aggregate_use_creates_pressure
    aggregate_pressure_check = {"check": "Global rules include aggregate_use_creates_pressure", "status": "PASS"}
    if "global_rules" not in registry_data or "aggregate_use_creates_pressure" not in registry_data["global_rules"]:
        aggregate_pressure_check["status"] = "FAIL"
        aggregate_pressure_check["reason"] = "'aggregate_use_creates_pressure' not found in global_rules."
    audit_results["checks"].append(aggregate_pressure_check)

    # Check 4: Global rules include wealth_does_not_cancel_residue
    wealth_residue_check = {"check": "Global rules include wealth_does_not_cancel_residue", "status": "PASS"}
    if "global_rules" not in registry_data or "wealth_does_not_cancel_residue" not in registry_data["global_rules"]:
        wealth_residue_check["status"] = "FAIL"
        wealth_residue_check["reason"] = "'wealth_does_not_cancel_residue' not found in global_rules."
    audit_results["checks"].append(wealth_residue_check)

    # Check 5: Global rules include no_single_resource_solves_all_systems
    no_single_resource_check = {"check": "Global rules include no_single_resource_solves_all_systems", "status": "PASS"}
    if "global_rules" not in registry_data or "no_single_resource_solves_all_systems" not in registry_data["global_rules"]:
        no_single_resource_check["status"] = "FAIL"
        no_single_resource_check["reason"] = "'no_single_resource_solves_all_systems' not found in global_rules."
    audit_results["checks"].append(no_single_resource_check)

    # Check 6: Operational cost profile schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Operational cost profile schema exists", "status": "PASS"})

    # Check 7: Example operational cost profile validates against schema
    example_validation_check = {"check": "Example operational cost profile validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_profile_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 8: Example includes gold_collected = 10000
    gold_collected_check = {"check": "Example includes gold_collected = 10000", "status": "PASS"}
    if example_profile_data.get("surface_loot_recent", {}).get("gold_collected") != 10000:
        gold_collected_check["status"] = "FAIL"
        gold_collected_check["reason"] = "'gold_collected' is not 10000 in example_operational_cost_profile.json."
    audit_results["checks"].append(gold_collected_check)

    # Check 9: Example includes potion or potion-like cost that appears small relative to loot
    potion_cost_check = {"check": "Example includes potion or potion-like cost that appears small relative to loot", "status": "PASS"}
    potions_cost = example_profile_data.get("recurring_costs", {}).get("potions", 0)
    gold_collected = example_profile_data.get("surface_loot_recent", {}).get("gold_collected", 1) # Avoid division by zero
    if not (potions_cost > 0 and (potions_cost / gold_collected) < 0.05): # Arbitrary threshold for "small"
        potion_cost_check["status"] = "FAIL"
        potion_cost_check["reason"] = "Potion cost is not small relative to gold collected, or not present."
    audit_results["checks"].append(potion_cost_check)

    # Check 10: Example indicates farming_needed = true
    farming_needed_check = {"check": "Example indicates farming_needed = true", "status": "PASS"}
    if example_profile_data.get("pressure_indicators", {}).get("farming_needed") is not True:
        farming_needed_check["status"] = "FAIL"
        farming_needed_check["reason"] = "'farming_needed' is not true in example_operational_cost_profile.json."
    audit_results["checks"].append(farming_needed_check)

    # Check 11: Example indicates risk_removed_by_wealth = false
    risk_removed_check = {"check": "Example indicates risk_removed_by_wealth = false", "status": "PASS"}
    if example_profile_data.get("pressure_indicators", {}).get("risk_removed_by_wealth") is not False:
        risk_removed_check["status"] = "FAIL"
        risk_removed_check["reason"] = "'risk_removed_by_wealth' is not false in example_operational_cost_profile.json."
    audit_results["checks"].append(risk_removed_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_010_operational_economy_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_010_operational_economy_result.json")

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
    audit = run_operational_economy_audit()
    print(json.dumps(audit, indent=2))
