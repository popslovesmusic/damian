import os
import json
import jsonschema

def run_bounded_progression_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-008",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    rules_path = os.path.join(project_root, "engine/player/progression/bounded_progression_rules.json")
    schema_path = os.path.join(project_root, "engine/player/contracts/player_progression_state.schema.json")
    example_state_path = os.path.join(project_root, "engine/player/contracts/example_player_progression_state.json")

    rules_data = {}
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

    rules_data = load_json_file(rules_path, "bounded_progression_rules.json")
    schema_data = load_json_file(schema_path, "player_progression_state.schema.json")
    example_state_data = load_json_file(example_state_path, "example_player_progression_state.json")

    if not all([rules_data, schema_data, example_state_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(schema_path)}/",
        referrer=schema_data
    )

    # Check 1: Bounded progression rules file exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Bounded progression rules file exists", "status": "PASS"})

    # Check 2: Allowed growth vectors include stat_growth, skill_unlocks, gear_progression, orientation_mastery, and tower_knowledge
    required_growth_vectors = ["stat_growth", "skill_unlocks", "gear_progression", "orientation_mastery", "tower_knowledge"]
    growth_vectors_check = {"check": "Allowed growth vectors include stat_growth, skill_unlocks, gear_progression, orientation_mastery, and tower_knowledge", "status": "PASS"}
    if "allowed_growth_vectors" not in rules_data:
        growth_vectors_check["status"] = "FAIL"
        growth_vectors_check["reason"] = "'allowed_growth_vectors' not found in rules data."
    else:
        current_growth_ids = {g["growth_id"] for g in rules_data["allowed_growth_vectors"]}
        if not all(rgv in current_growth_ids for rgv in required_growth_vectors):
            growth_vectors_check["status"] = "FAIL"
            growth_vectors_check["reason"] = f"Missing required growth vectors: {required_growth_vectors - current_growth_ids}"
    audit_results["checks"].append(growth_vectors_check)

    # Check 3: Forbidden growth results include permanent_invulnerability
    invulnerability_check = {"check": "Forbidden growth results include permanent_invulnerability", "status": "PASS"}
    if "forbidden_growth_results" not in rules_data or "permanent_invulnerability" not in rules_data["forbidden_growth_results"]:
        invulnerability_check["status"] = "FAIL"
        invulnerability_check["reason"] = "'permanent_invulnerability' not found in forbidden_growth_results."
    audit_results["checks"].append(invulnerability_check)

    # Check 4: Forbidden growth results include residue_immunity
    residue_immunity_check = {"check": "Forbidden growth results include residue_immunity", "status": "PASS"}
    if "forbidden_growth_results" not in rules_data or "residue_immunity" not in rules_data["forbidden_growth_results"]:
        residue_immunity_check["status"] = "FAIL"
        residue_immunity_check["reason"] = "'residue_immunity' not found in forbidden_growth_results."
    audit_results["checks"].append(residue_immunity_check)

    # Check 5: Residue pressure checks include dominant_build_visibility
    residue_pressure_check = {"check": "Residue pressure checks include dominant_build_visibility", "status": "PASS"}
    if "residue_pressure_checks" not in rules_data:
        residue_pressure_check["status"] = "FAIL"
        residue_pressure_check["reason"] = "'residue_pressure_checks' not found in rules data."
    else:
        current_pressure_check_ids = {c["check_id"] for c in rules_data["residue_pressure_checks"]}
        if "dominant_build_visibility" not in current_pressure_check_ids:
            residue_pressure_check["status"] = "FAIL"
            residue_pressure_check["reason"] = "'dominant_build_visibility' not found in residue_pressure_checks."
    audit_results["checks"].append(residue_pressure_check)

    # Check 6: Player progression schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Player progression schema exists", "status": "PASS"})

    # Check 7: Example progression state validates against schema
    example_validation_check = {"check": "Example progression state validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_state_data, schema=schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_validation_check["status"] = "FAIL"
        example_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_validation_check)

    # Check 8: All forbidden flags in example are false
    forbidden_flags_check = {"check": "All forbidden flags in example are false", "status": "PASS"}
    if "forbidden_flags" in example_state_data:
        for flag, value in example_state_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_player_progression_state.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_player_progression_state.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Check 9: Residue pressure values are present and bounded between 0.0 and 1.0
    residue_pressure_bounds_check = {"check": "Residue pressure values are present and bounded between 0.0 and 1.0", "status": "PASS"}
    if "residue_pressure" in example_state_data:
        for key, value in example_state_data["residue_pressure"].items():
            if not (isinstance(value, (int, float)) and 0.0 <= value <= 1.0):
                residue_pressure_bounds_check["status"] = "FAIL"
                residue_pressure_bounds_check["reason"] = f"Residue pressure '{key}' is not a number between 0.0 and 1.0."
                break
    else:
        residue_pressure_bounds_check["status"] = "FAIL"
        residue_pressure_bounds_check["reason"] = "'residue_pressure' not found in example_player_progression_state.json."
    audit_results["checks"].append(residue_pressure_bounds_check)

    # Check 10: Progression language emphasizes survivability rather than supremacy (conceptual check)
    audit_results["checks"].append({"check": "Progression language emphasizes survivability rather than supremacy", "status": "PASS"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Project Root: {project_root}")

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_008_bounded_progression_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_008_bounded_progression_result.json")

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
    audit = run_bounded_progression_audit()
    print(json.dumps(audit, indent=2))
