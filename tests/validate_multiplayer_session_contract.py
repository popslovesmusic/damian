import os
import json
import jsonschema

def run_multiplayer_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-011",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Paths to files
    registry_path = os.path.join(project_root, "engine/network/registry/multiplayer_mode_registry.json")
    session_schema_path = os.path.join(project_root, "engine/network/contracts/multiplayer_session.schema.json")
    invasion_schema_path = os.path.join(project_root, "engine/network/contracts/domain_invasion_event.schema.json")
    example_session_path = os.path.join(project_root, "engine/network/contracts/example_multiplayer_session.json")
    example_invasion_path = os.path.join(project_root, "engine/network/contracts/example_domain_invasion_event.json")

    registry_data = {}
    session_schema_data = {}
    invasion_schema_data = {}
    example_session_data = {}
    example_invasion_data = {}

    # Load files
    def load_json_file(file_path, description):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            audit_results["checks"].append({"check": f"Load {description}", "status": "FAIL", "reason": str(e)})
            return None

    registry_data = load_json_file(registry_path, "multiplayer_mode_registry.json")
    session_schema_data = load_json_file(session_schema_path, "multiplayer_session.schema.json")
    invasion_schema_data = load_json_file(invasion_schema_path, "domain_invasion_event.schema.json")
    example_session_data = load_json_file(example_session_path, "example_multiplayer_session.json")
    example_invasion_data = load_json_file(example_invasion_path, "example_domain_invasion_event.json")

    if not all([registry_data, session_schema_data, invasion_schema_data, example_session_data, example_invasion_data]):
        return audit_results

    # Add schemas to a resolver for cross-referencing (not strictly needed here but good practice)
    resolver = jsonschema.RefResolver(
        base_uri=f"file://{os.path.dirname(session_schema_path)}/",
        referrer=session_schema_data
    )

    # Check 1: Multiplayer mode registry exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Multiplayer mode registry exists", "status": "PASS"})

    # Check 2: Supported modes include private_coop, domain_invasion, and domain_defense
    supported_modes_check = {"check": "Supported modes include private_coop, domain_invasion, and domain_defense", "status": "PASS"}
    required_modes = {"private_coop", "domain_invasion", "domain_defense"}
    current_modes = {m.get("mode_id") for m in registry_data.get("supported_modes", [])}
    if not required_modes.issubset(current_modes):
        supported_modes_check["status"] = "FAIL"
        supported_modes_check["reason"] = f"Missing required modes: {required_modes - current_modes}."
    audit_results["checks"].append(supported_modes_check)

    # Check 3: Authority model declares server_authoritative as preferred
    authority_model_check = {"check": "Authority model declares server_authoritative as preferred", "status": "PASS"}
    if registry_data.get("authority_model", {}).get("preferred") != "server_authoritative":
        authority_model_check["status"] = "FAIL"
        authority_model_check["reason"] = "Preferred authority model is not 'server_authoritative'."
    audit_results["checks"].append(authority_model_check)

    # Check 4: Session schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Session schema exists", "status": "PASS"})

    # Check 5: Domain invasion event schema exists (handled by load_json_file)
    audit_results["checks"].append({"check": "Domain invasion event schema exists", "status": "PASS"})

    # Check 6: Example multiplayer session validates against schema
    example_session_validation_check = {"check": "Example multiplayer session validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_session_data, schema=session_schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_session_validation_check["status"] = "FAIL"
        example_session_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_session_validation_check["status"] = "FAIL"
        example_session_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_session_validation_check)

    # Check 7: Example domain invasion event validates against schema
    example_invasion_validation_check = {"check": "Example domain invasion event validates against schema", "status": "PASS"}
    try:
        jsonschema.validate(instance=example_invasion_data, schema=invasion_schema_data, resolver=resolver)
    except jsonschema.ValidationError as e:
        example_invasion_validation_check["status"] = "FAIL"
        example_invasion_validation_check["reason"] = f"Validation Error: {e.message}"
    except Exception as e:
        example_invasion_validation_check["status"] = "FAIL"
        example_invasion_validation_check["reason"] = f"Unexpected error during validation: {e}"
    audit_results["checks"].append(example_invasion_validation_check)

    # Check 8: Session player_ids are limited to 1-4 players
    player_ids_limit_check = {"check": "Session player_ids are limited to 1-4 players", "status": "PASS"}
    player_count = len(example_session_data.get("player_ids", []))
    if not (1 <= player_count <= 4):
        player_ids_limit_check["status"] = "FAIL"
        player_ids_limit_check["reason"] = f"Player count is {player_count}, not within 1-4 range."
    audit_results["checks"].append(player_ids_limit_check)

    # Check 9: Example uses safe_resolution_required = true
    safe_resolution_check = {"check": "Example uses safe_resolution_required = true", "status": "PASS"}
    if example_session_data.get("safe_resolution_required") is not True:
        safe_resolution_check["status"] = "FAIL"
        safe_resolution_check["reason"] = "'safe_resolution_required' is not true in example_multiplayer_session.json."
    audit_results["checks"].append(safe_resolution_check)

    # Check 10: Example invasion writes residue to attacker and defender
    invasion_residue_check = {"check": "Example invasion writes residue to attacker and defender", "status": "PASS"}
    if not (example_invasion_data.get("residue_written_to_attacker") is True and
            example_invasion_data.get("residue_written_to_defender") is True):
        invasion_residue_check["status"] = "FAIL"
        invasion_residue_check["reason"] = "Residue not written to both attacker and defender in example_domain_invasion_event.json."
    audit_results["checks"].append(invasion_residue_check)

    # Check 11: Example attacker advantage has attacker risk
    attacker_risk_check = {"check": "Example attacker advantage has attacker risk", "status": "PASS"}
    if example_invasion_data.get("attacker_advantage_used") and not example_invasion_data.get("attacker_risk_incurred"):
        attacker_risk_check["status"] = "FAIL"
        attacker_risk_check["reason"] = "Attacker advantage used but no attacker risk incurred."
    audit_results["checks"].append(attacker_risk_check)

    # Check 12: Example defender advantage has defender risk
    defender_risk_check = {"check": "Example defender advantage has defender risk", "status": "PASS"}
    if example_invasion_data.get("defender_advantage_active") and not example_invasion_data.get("defender_risk_incurred"):
        defender_risk_check["status"] = "FAIL"
        defender_risk_check["reason"] = "Defender advantage active but no defender risk incurred."
    audit_results["checks"].append(defender_risk_check)

    # Check 13: Example forbidden flags are all false
    forbidden_flags_check = {"check": "Example forbidden flags are all false", "status": "PASS"}
    if "forbidden_flags" in example_invasion_data:
        for flag, value in example_invasion_data["forbidden_flags"].items():
            if value is not False:
                forbidden_flags_check["status"] = "FAIL"
                forbidden_flags_check["reason"] = f"Forbidden flag '{flag}' is true in example_domain_invasion_event.json."
                break
    else:
        forbidden_flags_check["status"] = "FAIL"
        forbidden_flags_check["reason"] = "'forbidden_flags' not found in example_domain_invasion_event.json."
    audit_results["checks"].append(forbidden_flags_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_011_multiplayer_contract_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_011_multiplayer_contract_result.json")

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
    audit = run_multiplayer_audit()
    print(json.dumps(audit, indent=2))
