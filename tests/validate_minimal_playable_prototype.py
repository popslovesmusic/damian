import os
import json
import jsonschema

def run_prototype_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-016",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    boundary_path = os.path.join(project_root, "engine/prototype/minimal_playable_boundary.json")
    schema_path = os.path.join(project_root, "engine/prototype/contracts/prototype_readiness_check.schema.json")
    example_check_path = os.path.join(project_root, "engine/prototype/contracts/example_prototype_readiness_check.json")

    boundary_data = {}
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

    boundary_data = load_json_file(boundary_path, "minimal_playable_boundary.json")
    schema_data = load_json_file(schema_path, "prototype_readiness_check.schema.json")
    example_check_data = load_json_file(example_check_path, "example_prototype_readiness_check.json")

    if not all([boundary_data, schema_data, example_check_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Minimal playable boundary file exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Minimal playable boundary file exists", "status": "PASS"})

    # Check 2: Prototype includes exactly 3 floors
    floors_check = {"check": "Prototype includes exactly 3 floors", "status": "PASS"}
    if boundary_data.get("prototype_limits", {}).get("floors") != 3:
        floors_check["status"] = "FAIL"
        floors_check["reason"] = "Prototype limits for 'floors' is not 3."
    audit_results["checks"].append(floors_check)

    # Check 3: Prototype includes exactly 3 enemy types
    enemy_types_check = {"check": "Prototype includes exactly 3 enemy types", "status": "PASS"}
    if boundary_data.get("prototype_limits", {}).get("enemy_types") != 3:
        enemy_types_check["status"] = "FAIL"
        enemy_types_check["reason"] = "Prototype limits for 'enemy_types' is not 3."
    audit_results["checks"].append(enemy_types_check)

    # Check 4: Prototype includes exactly 1 boss
    bosses_check = {"check": "Prototype includes exactly 1 boss", "status": "PASS"}
    if boundary_data.get("prototype_limits", {}).get("bosses") != 1:
        bosses_check["status"] = "FAIL"
        bosses_check["reason"] = "Prototype limits for 'bosses' is not 1."
    audit_results["checks"].append(bosses_check)

    # Check 5: Prototype includes defeat_drop_one_floor
    defeat_drop_check = {"check": "Prototype includes defeat_drop_one_floor", "status": "PASS"}
    if "defeat_drop_one_floor" not in boundary_data.get("included_systems", []):
        defeat_drop_check["status"] = "FAIL"
        defeat_drop_check["reason"] = "'defeat_drop_one_floor' not found in included_systems."
    audit_results["checks"].append(defeat_drop_check)

    # Check 6: Prototype includes basic_residue_capture
    residue_capture_check = {"check": "Prototype includes basic_residue_capture", "status": "PASS"}
    if "basic_residue_capture" not in boundary_data.get("included_systems", []):
        residue_capture_check["status"] = "FAIL"
        residue_capture_check["reason"] = "'basic_residue_capture' not found in included_systems."
    audit_results["checks"].append(residue_capture_check)

    # Check 7: Prototype includes basic_floor_mutation
    floor_mutation_check = {"check": "Prototype includes basic_floor_mutation", "status": "PASS"}
    if "basic_floor_mutation" not in boundary_data.get("included_systems", []):
        floor_mutation_check["status"] = "FAIL"
        floor_mutation_check["reason"] = "'basic_floor_mutation' not found in included_systems."
    audit_results["checks"].append(floor_mutation_check)

    # Check 8: Prototype excludes live multiplayer
    excluded_multiplayer_check = {"check": "Prototype excludes live multiplayer", "status": "PASS"}
    if "live_multiplayer" not in boundary_data.get("excluded_systems", []):
        excluded_multiplayer_check["status"] = "FAIL"
        excluded_multiplayer_check["reason"] = "'live_multiplayer' not found in excluded_systems."
    audit_results["checks"].append(excluded_multiplayer_check)

    # Check 9: Prototype excludes domain dashboard UI
    excluded_dashboard_check = {"check": "Prototype excludes domain dashboard UI", "status": "PASS"}
    if "domain_dashboard_ui" not in boundary_data.get("excluded_systems", []):
        excluded_dashboard_check["status"] = "FAIL"
        excluded_dashboard_check["reason"] = "'domain_dashboard_ui' not found in excluded_systems."
    audit_results["checks"].append(excluded_dashboard_check)

    # Check 10: Readiness check schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Readiness check schema exists", "status": "PASS"})

    # Check 11: Example readiness check validates against schema
    example_validation_check = {"check": "Example readiness check validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_check_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 12: Example ready_for_runtime_implementation = true
    ready_for_runtime_check = {"check": "Example ready_for_runtime_implementation = true", "status": "PASS"}
    if example_check_data.get("ready_for_runtime_implementation") is not True:
        ready_for_runtime_check["status"] = "FAIL"
        ready_for_runtime_check["reason"] = "'ready_for_runtime_implementation' is not true in example_prototype_readiness_check.json."
    audit_results["checks"].append(ready_for_runtime_check)

    # Check 13: Example scope_creep_detected = false
    scope_creep_check = {"check": "Example scope_creep_detected = false", "status": "PASS"}
    if example_check_data.get("scope_creep_detected") is not False:
        scope_creep_check["status"] = "FAIL"
        scope_creep_check["reason"] = "'scope_creep_detected' is not false in example_prototype_readiness_check.json."
    audit_results["checks"].append(scope_creep_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_016_prototype_boundary_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_016_prototype_boundary_result.json")

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
    audit = run_prototype_audit()
    print(json.dumps(audit, indent=2))
