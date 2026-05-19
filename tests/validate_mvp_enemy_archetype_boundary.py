import os
import json
import jsonschema

def run_enemy_archetype_boundary_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-046",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths
    registry_path = os.path.join(project_root, "engine/enemies/enemy_archetype_registry.json")
    schema_path = os.path.join(project_root, "engine/enemies/contracts/enemy_archetype.schema.json")
    example_path = os.path.join(project_root, "engine/enemies/contracts/example_enemy_archetype.json")

    # Load files
    def load_json_file(file_path, description):
        try:
            if not os.path.exists(file_path):
                audit_results["checks"].append({"check": f"{description} exists", "status": "FAIL", "reason": "File not found"})
                return None
            with open(file_path, 'r') as f:
                data = json.load(f)
                audit_results["checks"].append({"check": f"{description} exists", "status": "PASS"})
                return data
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "enemy_archetype_registry.json")
    schema_data = load_json_file(schema_path, "enemy_archetype.schema.json")
    example_data = load_json_file(example_path, "example_enemy_archetype.json")

    if not all([registry_data, schema_data, example_data]):
        write_results(project_root, audit_results)
        return audit_results

    # Check 1: Registry declares at least 4 archetypes
    archetypes = registry_data.get("archetypes", [])
    registry_count_check = {"check": "Registry declares at least 4 archetypes", "status": "PASS"}
    if len(archetypes) < 4:
        registry_count_check["status"] = "FAIL"
        registry_count_check["reason"] = f"Found only {len(archetypes)} archetypes"
    audit_results["checks"].append(registry_count_check)

    # Check 2: Registry includes specific archetypes
    expected_ids = ["pressure_unit", "ambush_unit", "attrition_unit", "counter_unit"]
    actual_ids = [a["enemy_archetype_id"] for a in archetypes]
    registry_ids_check = {"check": "Registry includes required archetypes", "status": "PASS"}
    missing_ids = [eid for eid in expected_ids if eid not in actual_ids]
    if missing_ids:
        registry_ids_check["status"] = "FAIL"
        registry_ids_check["reason"] = f"Missing archetypes: {', '.join(missing_ids)}"
    audit_results["checks"].append(registry_ids_check)

    # Check 3: Global rules checks
    rules = registry_data.get("global_rules", [])
    rules_check = {"check": "Registry includes core global rules", "status": "PASS"}
    required_rules = ["enemy_power_must_be_bounded", "enemy_pressure_must_not_bypass_pipeline"]
    missing_rules = [r for r in required_rules if r not in rules]
    if missing_rules:
        rules_check["status"] = "FAIL"
        rules_check["reason"] = f"Missing rules: {', '.join(missing_rules)}"
    audit_results["checks"].append(rules_check)

    # Check 4: Example validates against schema
    example_schema_check = {"check": "Example enemy archetype validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_data, schema=schema_data)
    except jsonschema.ValidationError as e:
        example_schema_check["status"] = "FAIL"
        example_schema_check["reason"] = f"Validation Error: {e.message}"
    audit_results["checks"].append(example_schema_check)

    # Check 5: Example rating and triggers
    rating_check = {"check": "Example rating and triggers are valid", "status": "PASS"}
    if not (0.0 <= example_data.get("base_pressure_rating", -1) <= 1.0):
        rating_check["status"] = "FAIL"
        rating_check["reason"] = "base_pressure_rating out of range"
    if not example_data.get("residue_triggers"):
        rating_check["status"] = "FAIL"
        rating_check["reason"] = "residue_triggers missing or empty"
    audit_results["checks"].append(rating_check)

    # Check 6: Bounded rules are false
    bounded_check = {"check": "Example bounded_rules are all false", "status": "PASS"}
    br = example_data.get("bounded_rules", {})
    if any(br.values()):
        bounded_check["status"] = "FAIL"
        bounded_check["reason"] = f"Some bounded rules are True: {br}"
    audit_results["checks"].append(bounded_check)

    # Check 7: No forbidden code
    runtime_check = {"check": "No forbidden systems introduced", "status": "PASS"}
    forbidden_dirs = ["engine/enemies/runtime", "engine/enemies/ai"]
    for d in forbidden_dirs:
        if os.path.exists(os.path.join(project_root, d)):
            runtime_check["status"] = "FAIL"
            runtime_check["reason"] = f"Forbidden directory exists: {d}"
    audit_results["checks"].append(runtime_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    write_results(project_root, audit_results)
    return audit_results

def write_results(project_root, audit_results):
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_046_enemy_archetype_boundary_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_046_enemy_archetype_boundary_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_enemy_archetype_boundary_audit()
    print(json.dumps(audit, indent=2))
