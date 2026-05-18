import os
import json
import jsonschema

def run_floor_identity_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-006",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    rules_path = os.path.join(project_root, "engine/floor_generation/identity/floor_identity_preservation_rules.json")
    schema_path = os.path.join(project_root, "engine/floor_generation/contracts/floor_identity_check.schema.json")
    example_check_path = os.path.join(project_root, "engine/floor_generation/contracts/example_floor_identity_check.json")

    rules_data = {}
    schema_data = {}
    example_check_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    rules_data = load_json_file(rules_path, "floor_identity_preservation_rules.json")
    schema_data = load_json_file(schema_path, "floor_identity_check.schema.json")
    example_check_data = load_json_file(example_check_path, "example_floor_identity_check.json")

    if not all([rules_data, schema_data, example_check_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Identity preservation rules file exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Identity preservation rules file exists", "status": "PASS"})

    # Check 2: At least 7 required identity anchors are declared
    anchors_count_check = {"check": "At least 7 required identity anchors are declared", "status": "PASS"}
    if not rules_data or "required_identity_anchors" not in rules_data or len(rules_data["required_identity_anchors"]) < 7:
        anchors_count_check["status"] = "FAIL"
        anchors_count_check["reason"] = "Rules file missing or has less than 7 required identity anchors."
    audit_results["checks"].append(anchors_count_check)

    # Check 3: Forbidden mutation results include all_routes_blocked
    all_routes_blocked_check = {"check": "Forbidden mutation results include all_routes_blocked", "status": "PASS"}
    if "forbidden_mutation_results" not in rules_data or "all_routes_blocked" not in rules_data["forbidden_mutation_results"]:
        all_routes_blocked_check["status"] = "FAIL"
        all_routes_blocked_check["reason"] = "'all_routes_blocked' not found in forbidden_mutation_results."
    audit_results["checks"].append(all_routes_blocked_check)

    # Check 4: Forbidden mutation results include full_floor_replacement
    full_floor_replacement_check = {"check": "Forbidden mutation results include full_floor_replacement", "status": "PASS"}
    if "forbidden_mutation_results" not in rules_data or "full_floor_replacement" not in rules_data["forbidden_mutation_results"]:
        full_floor_replacement_check["status"] = "FAIL"
        full_floor_replacement_check["reason"] = "'full_floor_replacement' not found in forbidden_mutation_results."
    audit_results["checks"].append(full_floor_replacement_check)

    # Check 5: Identity check schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Identity check schema exists", "status": "PASS"})

    # Check 6: Example identity check validates against schema
    example_validation_check = {"check": "Example identity check validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_check_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 7: Example has entry_reachable = true
    entry_reachable_check = {"check": "Example has entry_reachable = true", "status": "PASS"}
    if example_check_data.get("entry_reachable") is not True:
        entry_reachable_check["status"] = "FAIL"
        entry_reachable_check["reason"] = "'entry_reachable' is not true in example_floor_identity_check.json."
    audit_results["checks"].append(entry_reachable_check)

    # Check 8: Example has exit_reachable = true
    exit_reachable_check = {"check": "Example has exit_reachable = true", "status": "PASS"}
    if example_check_data.get("exit_reachable") is not True:
        exit_reachable_check["status"] = "FAIL"
        exit_reachable_check["reason"] = "'exit_reachable' is not true in example_floor_identity_check.json."
    audit_results["checks"].append(exit_reachable_check)

    # Check 9: Example has primary_route_exists = true
    primary_route_exists_check = {"check": "Example has primary_route_exists = true", "status": "PASS"}
    if example_check_data.get("primary_route_exists") is not True:
        primary_route_exists_check["status"] = "FAIL"
        primary_route_exists_check["reason"] = "'primary_route_exists' is not true in example_floor_identity_check.json."
    audit_results["checks"].append(primary_route_exists_check)

    # Check 10: Example has playability_preserved = true
    playability_preserved_check = {"check": "Example has playability_preserved = true", "status": "PASS"}
    if example_check_data.get("playability_preserved") is not True:
        playability_preserved_check["status"] = "FAIL"
        playability_preserved_check["reason"] = "'playability_preserved' is not true in example_floor_identity_check.json."
    audit_results["checks"].append(playability_preserved_check)

    # Check 11: Example identity_status is PRESERVED or WEAKENED_BUT_VALID
    identity_status_check = {"check": "Example identity_status is PRESERVED or WEAKENED_BUT_VALID", "status": "PASS"}
    identity_status = example_check_data.get("identity_status")
    if identity_status not in ["PRESERVED", "WEAKENED_BUT_VALID"]:
        identity_status_check["status"] = "FAIL"
        identity_status_check["reason"] = f"identity_status '{identity_status}' is not 'PRESERVED' or 'WEAKENED_BUT_VALID'."
    audit_results["checks"].append(identity_status_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Project Root: {project_root}")

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_006_floor_identity_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_006_floor_identity_result.json")

    print(f"Attempting to write audit to: {audit_file_path}")
    try:
        with open(audit_file_path, 'w') as f:
            json.dump(audit_results, f, indent=2)
        print(f"Successfully wrote audit to {audit_file_path}")
    except Exception as e:
        print(f"ERROR: Failed to write audit file {audit_file_path}: {e}")

    print(f"Attempting to write validation results to: {result_file_path}")
    try:
        with open(result_file_path, 'w') as f:
            json.dump({"verdict": audit_results["verdict"]}, f, indent=2)
        print(f"Successfully wrote validation results to {result_file_path}")
    except Exception as e:
        print(f"ERROR: Failed to write result file {result_file_path}: {e}")

    print(f"Audit results written to {audit_file_path}")
    print(f"Validation results written to {result_file_path}")
    return audit_results

if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema library not found. Please install it: pip install jsonschema")
        exit(1)
    audit = run_floor_identity_audit()
    print(json.dumps(audit, indent=2))
