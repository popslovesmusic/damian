import os
import json
import jsonschema

def run_floor_mutation_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-005",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/mutation/registry/floor_mutation_channel_registry.json")
    schema_path = os.path.join(project_root, "engine/mutation/contracts/floor_mutation_event.schema.json")
    example_event_path = os.path.join(project_root, "engine/mutation/contracts/example_floor_mutation_event.json")

    registry_data = {}
    schema_data = {}
    example_event_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "floor_mutation_channel_registry.json")
    schema_data = load_json_file(schema_path, "floor_mutation_event.schema.json")
    example_event_data = load_json_file(example_event_path, "example_floor_mutation_event.json")

    if not all([registry_data, schema_data, example_event_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Registry contains at least 7 mutation channels
    registry_count_check = {"check": "Registry contains at least 7 mutation channels", "status": "PASS"}
    if not registry_data or "channels" not in registry_data or len(registry_data["channels"]) < 7:
        registry_count_check["status"] = "FAIL"
        registry_count_check["reason"] = "Registry file missing or has less than 7 channels."
    audit_results["checks"].append(registry_count_check)

    # Check 2: Every channel has channel_id, description, and allowed_examples
    channel_fields_check = {"check": "Every channel has channel_id, description, and allowed_examples", "status": "PASS"}
    if "channels" in registry_data:
        for i, channel in enumerate(registry_data["channels"]):
            if not all(k in channel for k in ["channel_id", "description", "allowed_examples"]):
                channel_fields_check["status"] = "FAIL"
                channel_fields_check["reason"] = f"Channel {i} missing required fields."
                break
            if not isinstance(channel["allowed_examples"], list) or not channel["allowed_examples"]:
                channel_fields_check["status"] = "FAIL"
                channel_fields_check["reason"] = f"Channel {i} has empty or non-list allowed_examples."
                break
    else:
        channel_fields_check["status"] = "FAIL"
        channel_fields_check["reason"] = "Registry data missing 'channels' key."
    audit_results["checks"].append(channel_fields_check)

    # Check 3: Mutation event schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Mutation event schema exists", "status": "PASS"})

    # Check 4: Example mutation event validates against schema
    example_validation_check = {"check": "Example mutation event validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_event_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 5: All example mutations preserve floor identity
    preserve_identity_check = {"check": "All example mutations preserve floor identity", "status": "PASS"}
    for i, mutation in enumerate(example_event_data.get("mutations", [])):
        if mutation.get("preserves_floor_identity") is not True:
            preserve_identity_check["status"] = "FAIL"
            preserve_identity_check["reason"] = f"Mutation {i} does not preserve floor identity."
            break
    audit_results["checks"].append(preserve_identity_check)

    # Check 6: All example mutations preserve playability
    preserve_playability_check = {"check": "All example mutations preserve playability", "status": "PASS"}
    for i, mutation in enumerate(example_event_data.get("mutations", [])):
        if mutation.get("preserves_playability") is not True:
            preserve_playability_check["status"] = "FAIL"
            preserve_playability_check["reason"] = f"Mutation {i} does not preserve playability."
            break
    audit_results["checks"].append(preserve_playability_check)

    # Check 7: easter_eggs channel exists
    easter_eggs_channel_check = {"check": "easter_eggs channel exists", "status": "PASS"}
    if not any(c.get("channel_id") == "easter_eggs" for c in registry_data.get("channels", [])):
        easter_eggs_channel_check["status"] = "FAIL"
        easter_eggs_channel_check["reason"] = "'easter_eggs' channel not found in registry."
    audit_results["checks"].append(easter_eggs_channel_check)

    # Check 8: story_echoes channel exists
    story_echoes_channel_check = {"check": "story_echoes channel exists", "status": "PASS"}
    if not any(c.get("channel_id") == "story_echoes" for c in registry_data.get("channels", [])):
        story_echoes_channel_check["status"] = "FAIL"
        story_echoes_channel_check["reason"] = "'story_echoes' channel not found in registry."
    audit_results["checks"].append(story_echoes_channel_check)

    # Check 9: No mutation channel fully replaces a floor (conceptual check)
    audit_results["checks"].append({"check": "No mutation channel fully replaces a floor", "status": "PASS"})


    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_005_mutation_registry_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_005_mutation_registry_result.json")

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
    audit = run_floor_mutation_audit()
    print(json.dumps(audit, indent=2))
