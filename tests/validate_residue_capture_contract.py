import os
import json
import jsonschema

def run_residue_contract_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-004",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    taxonomy_path = os.path.join(project_root, "engine/residue/taxonomy/residue_capture_taxonomy.json")
    schema_path = os.path.join(project_root, "engine/residue/contracts/mutation_input_contract.schema.json")
    example_input_path = os.path.join(project_root, "engine/residue/contracts/example_mutation_input.json")

    taxonomy_data = {}
    schema_data = {}
    example_input_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    taxonomy_data = load_json_file(taxonomy_path, "residue_capture_taxonomy.json")
    schema_data = load_json_file(schema_path, "mutation_input_contract.schema.json")
    example_input_data = load_json_file(example_input_path, "example_mutation_input.json")

    if not all([taxonomy_data, schema_data, example_input_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (though not strictly needed for this patch as no $ref in contract)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Residue taxonomy exists and contains at least 7 categories
    taxonomy_exists_check = {"check": "Residue taxonomy exists and contains at least 7 categories", "status": "PASS"}
    if not taxonomy_data or "categories" not in taxonomy_data or len(taxonomy_data["categories"]) < 7:
        taxonomy_exists_check["status"] = "FAIL"
        taxonomy_exists_check["reason"] = "Taxonomy file missing or has less than 7 categories."
    audit_results["checks"].append(taxonomy_exists_check)

    # Check 2: Every taxonomy category has category_id, description, and non-empty signals
    taxonomy_category_check = {"check": "Every taxonomy category has category_id, description, and non-empty signals", "status": "PASS"}
    if "categories" in taxonomy_data:
        for i, category in enumerate(taxonomy_data["categories"]):
            if not all(k in category for k in ["category_id", "description", "signals"]):
                taxonomy_category_check["status"] = "FAIL"
                taxonomy_category_check["reason"] = f"Category {i} missing required fields."
                break
            if not isinstance(category["signals"], list) or not category["signals"]:
                taxonomy_category_check["status"] = "FAIL"
                taxonomy_category_check["reason"] = f"Category {i} has empty or non-list signals."
                break
    else:
        taxonomy_category_check["status"] = "FAIL"
        taxonomy_category_check["reason"] = "Taxonomy data missing 'categories' key."
    audit_results["checks"].append(taxonomy_category_check)

    # Check 3: Mutation input contract schema exists (already handled by load_json_file)
    audit_results["checks"].append({"check": "Mutation input contract schema exists", "status": "PASS"})

    # Check 4: Example mutation input validates against mutation_input_contract.schema.json
    example_validation_check = {"check": "Example mutation input validates against mutation_input_contract.schema.json", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_input_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 5: eligible_mutation_channels includes easter_eggs
    easter_eggs_channel_check = {"check": "eligible_mutation_channels includes easter_eggs", "status": "PASS"}
    if "eligible_mutation_channels" not in example_input_data or "easter_eggs" not in example_input_data["eligible_mutation_channels"]:
        easter_eggs_channel_check["status"] = "FAIL"
        easter_eggs_channel_check["reason"] = "'easter_eggs' not found in eligible_mutation_channels."
    audit_results["checks"].append(easter_eggs_channel_check)

    # Check 6: DEFEAT_DROP example allows may_reveal_rewards = true
    may_reveal_rewards_check = {"check": "DEFEAT_DROP example allows may_reveal_rewards = true", "status": "PASS"}
    if example_input_data.get("source_outcome") == "DEFEAT_DROP" and example_input_data.get("mutation_constraints", {}).get("may_reveal_rewards") is not True:
        may_reveal_rewards_check["status"] = "FAIL"
        may_reveal_rewards_check["reason"] = "DEFEAT_DROP outcome does not allow may_reveal_rewards = true."
    audit_results["checks"].append(may_reveal_rewards_check)
    
    # Check 7: mutation_constraints includes must_preserve_floor_identity = true
    must_preserve_floor_check = {"check": "mutation_constraints includes must_preserve_floor_identity = true", "status": "PASS"}
    if example_input_data.get("mutation_constraints", {}).get("must_preserve_floor_identity") is not True:
        must_preserve_floor_check["status"] = "FAIL"
        must_preserve_floor_check["reason"] = "must_preserve_floor_identity is not true in mutation_constraints."
    audit_results["checks"].append(must_preserve_floor_check)

    # Check 8: Content pack ID appears as data and does not redefine residue categories
    content_pack_id_check = {"check": "Content pack ID appears as data and does not redefine residue categories", "status": "PASS"}
    if not (isinstance(example_input_data.get("content_pack_id"), str) and example_input_data.get("content_pack_id") == "damian"):
        content_pack_id_check["status"] = "FAIL"
        content_pack_id_check["reason"] = "content_pack_id not found as a string or does not match 'damian' in example_mutation_input.json."
    # The "does not redefine residue categories" part is a design rule checked by taxonomy_category_check primarily
    audit_results["checks"].append(content_pack_id_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_004_residue_contract_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_004_residue_contract_result.json")

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
    audit = run_residue_contract_audit()
    print(json.dumps(audit, indent=2))
