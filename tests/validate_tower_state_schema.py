import os
import json
import jsonschema

def run_persistence_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-003",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to schemas and example data
    tower_state_schema_path = os.path.join(project_root, "engine/save/schemas/tower_state.schema.json")
    floor_memory_schema_path = os.path.join(project_root, "engine/save/schemas/floor_memory.schema.json")
    residue_record_schema_path = os.path.join(project_root, "engine/save/schemas/residue_record.schema.json")
    example_tower_state_path = os.path.join(project_root, "engine/save/examples/example_tower_state.json")

    tower_state_schema = {}
    floor_memory_schema = {}
    residue_record_schema = {}
    example_tower_state_data = {}

    # Load schemas and example data
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    tower_state_schema = load_json_file(tower_state_schema_path, "tower_state.schema.json")
    floor_memory_schema = load_json_file(floor_memory_schema_path, "floor_memory.schema.json")
    residue_record_schema = load_json_file(residue_record_schema_path, "residue_record.schema.json")
    example_tower_state_data = load_json_file(example_tower_state_path, "example_tower_state.json")

    # If any essential file failed to load, return early
    if not all([tower_state_schema, floor_memory_schema, residue_record_schema, example_tower_state_data]):
        return audit_results
    
    # Add schemas to a resolver for cross-referencing
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(tower_state_schema_path)}/",
        referrer=tower_state_schema
    )

    # Check 1: All three schemas exist (already handled by load_json_file and early exit)
    audit_results["checks"].append({"check": "All three schemas exist", "status": "PASS"}) # If we reach here, they exist

    # Check 2: Example tower state validates against tower_state.schema.json
    tower_state_validation_check = {"check": "Example tower state validates against tower_state.schema.json", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_tower_state_data, schema=tower_state_schema, resolver=resolver)
    except jsonschema.ValidationError as e:
        tower_state_validation_check["status"] = "FAIL"
        tower_state_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        tower_state_validation_check["status"] = "FAIL"
        tower_state_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(tower_state_validation_check)

    # Check 3: floor_memory records validate against floor_memory.schema.json
    floor_memory_validation_check = {"check": "floor_memory records validate against floor_memory.schema.json", "status": "PASS"}
    if "floor_memory" in example_tower_state_data and example_tower_state_data["floor_memory"]:
        for i, floor_record in enumerate(example_tower_state_data["floor_memory"]):
            try:
                jsonschema.validate(instance=floor_record, schema=floor_memory_schema, resolver=resolver)
            except jsonschema.ValidationError as e:
                floor_memory_validation_check["status"] = "FAIL"
                floor_memory_validation_check["reason"] = f"Floor memory record {i} Validation Error: {e.message}"
                break
            except Exception as e:
                floor_memory_validation_check["status"] = "FAIL"
                floor_memory_validation_check["reason"] = f"Unexpected error validating floor memory record {i}: {e}"
                break
    audit_results["checks"].append(floor_memory_validation_check)

    # Check 4: residue_history records validate against residue_record.schema.json
    residue_history_validation_check = {"check": "residue_history records validate against residue_record.schema.json", "status": "PASS"}
    if "floor_memory" in example_tower_state_data and example_tower_state_data["floor_memory"]:
        for i, floor_record in enumerate(example_tower_state_data["floor_memory"]):
            if "residue_history" in floor_record and floor_record["residue_history"]:
                for j, residue_record in enumerate(floor_record["residue_history"]):
                    try:
                        jsonschema.validate(instance=residue_record, schema=residue_record_schema, resolver=resolver)
                    except jsonschema.ValidationError as e:
                        residue_history_validation_check["status"] = "FAIL"
                        residue_history_validation_check["reason"] = f"Residue record {j} in floor {i} Validation Error: {e.message}"
                        break
                    except Exception as e:
                        residue_history_validation_check["status"] = "FAIL"
                        residue_history_validation_check["reason"] = f"Unexpected error validating residue record {j} in floor {i}: {e}"
                        break
            if residue_history_validation_check["status"] == "FAIL":
                break # Stop checking if an error is found
    audit_results["checks"].append(residue_history_validation_check)


    # Check 5: current_floor <= highest_floor_reached
    floor_progress_check = {"check": "current_floor <= highest_floor_reached", "status": "PASS"}
    if example_tower_state_data.get("current_floor", 0) > example_tower_state_data.get("highest_floor_reached", 0):
        floor_progress_check["status"] = "FAIL"
        floor_progress_check["reason"] = "current_floor is greater than highest_floor_reached."
    audit_results["checks"].append(floor_progress_check)

    # Check 6: DEFEAT_DROP example includes mutation_triggered = true
    defeat_drop_mutation_check = {"check": "DEFEAT_DROP example includes mutation_triggered = true", "status": "PASS"}
    found_defeat_drop_with_mutation = False
    for floor_record in example_tower_state_data.get("floor_memory", []):
        for residue_record in floor_record.get("residue_history", []):
            if residue_record.get("outcome") == "DEFEAT_DROP" and residue_record.get("mutation_triggered") is True:
                found_defeat_drop_with_mutation = True
                break
        if found_defeat_drop_with_mutation:
            break
    if not found_defeat_drop_with_mutation:
        defeat_drop_mutation_check["status"] = "FAIL"
        defeat_drop_mutation_check["reason"] = "No DEFEAT_DROP residue record found with mutation_triggered = true."
    audit_results["checks"].append(defeat_drop_mutation_check)

    # Check 7: Floor memory supports discovered and unclaimed easter eggs
    # This is implicitly checked by schema validation.
    # The check is primarily to ensure the fields exist and are of correct type.
    easter_egg_support_check = {"check": "Floor memory supports discovered and unclaimed easter eggs", "status": "PASS"}
    for floor_record in example_tower_state_data.get("floor_memory", []):
        if not ("discovered_easter_eggs" in floor_record and isinstance(floor_record["discovered_easter_eggs"], list)):
            easter_egg_support_check["status"] = "FAIL"
            easter_egg_support_check["reason"] = "discovered_easter_eggs field missing or not a list in a floor memory record."
            break
        if not ("unclaimed_easter_eggs" in floor_record and isinstance(floor_record["unclaimed_easter_eggs"], list)):
            easter_egg_support_check["status"] = "FAIL"
            easter_egg_support_check["reason"] = "unclaimed_easter_eggs field missing or not a list in a floor memory record."
            break
    audit_results["checks"].append(easter_egg_support_check)


    # Check 8: Content pack ID appears as data, not schema override
    # This is a design principle, implicitly covered by the fact that the schemas are loaded
    # and the content_pack_id is just a string field in the tower_state.
    content_pack_id_check = {"check": "Content pack ID appears as data, not schema override", "status": "PASS"}
    if not (isinstance(example_tower_state_data.get("content_pack_id"), str) and example_tower_state_data.get("content_pack_id") == "damian"):
        content_pack_id_check["status"] = "FAIL"
        content_pack_id_check["reason"] = "content_pack_id not found as a string or does not match 'damian' in example_tower_state.json."
    audit_results["checks"].append(content_pack_id_check)


    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_003_persistence_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_003_persistence_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    print(f"Validation results written to {result_file_path}")
    return audit_results

if __name__ == "__main__":
    # Ensure jsonschema is installed
    try:
        import jsonschema
    except ImportError:
        print("jsonschema library not found. Please install it: pip install jsonschema")
        exit(1)
    audit = run_persistence_audit()
    print(json.dumps(audit, indent=2))
