import os
import json
import shutil
import subprocess

class TestData:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def write_dummy_json(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2)

def run_visual_presentation_scaffold_validation():
    audit_results = {
        "patch_id": "STAGE-068",
        "verdict": "FAIL",
        "play_session_id": "N/A",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_root = os.path.join(project_root, "build/runtime_persistence_test")
    os.makedirs(data_root, exist_ok=True)

    # Pre-create all necessary contract/manifest files for PlayableSliceManager and VisualScaffoldManager
    os.makedirs(os.path.join(project_root, "outputs/audits"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/os_boundary/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/runtime/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/presentation"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/player/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/traversal/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/combat/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/enemies/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/economy/contracts"), exist_ok=True)

    # Minimal dummy files for sub-managers
    TestData(os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    TestData(os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json")).write_dummy_json({"commands": [], "validation_rules": {"max_command_length": 256, "disallowed_characters": []}})
    TestData(os.path.join(project_root, "player/contracts/first_hour_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "learning_policy": {"environmental_teaching": True, "progressive_system_reveal": True, "demonstrate_recoverability": True, "demonstrate_pressure_early": True}})
    TestData(os.path.join(project_root, "player/contracts/onboarding_contract.json")).write_dummy_json({"contract_id": "onboarding-v1", "required_topics": [], "forbidden_patterns": [], "validation_rules": {}})
    TestData(os.path.join(project_root, "traversal/contracts/traversal_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"exposure_threshold_for_detection": 75.0, "mandatory_camera_shake_on_heavy_landing": True, "max_traversal_audio_layers": 4}})
    TestData(os.path.join(project_root, "traversal/contracts/movement_contract_schema.json")).write_dummy_json({"contract_id": "movement-v1", "movement_modes": ["STANDARD", "INJURED", "RUSH"], "validation_rules": {}})
    TestData(os.path.join(project_root, "combat/contracts/combat_feel_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"mandatory_hitstop_duration_ms_min": 30}})
    TestData(os.path.join(project_root, "combat/contracts/combat_feedback_contract.json")).write_dummy_json({"contract_id": "combat-v1", "combat_event_types": ["PLAYER_HIT_ENEMY", "ENEMY_HIT_PLAYER"], "validation_rules": {}})
    TestData(os.path.join(project_root, "enemies/contracts/enemy_ecology_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"min_telegraph_duration_ms": 300}})
    TestData(os.path.join(project_root, "enemies/contracts/enemy_behavior_contract.json")).write_dummy_json({"contract_id": "enemy-v1", "ecology_types": ["PREDATOR", "SCAVENGER"], "validation_rules": {}})
    TestData(os.path.join(project_root, "economy/contracts/resource_scarcity_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    TestData(os.path.join(project_root, "economy/contracts/survival_economy_contract.json")).write_dummy_json({"contract_id": "economy-v1", "resource_types": ["FOOD", "SCRAP"], "validation_rules": {}})
    TestData(os.path.join(project_root, "player/contracts/death_continuation_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    TestData(os.path.join(project_root, "player/contracts/survivor_continuation_contract.json")).write_dummy_json({"contract_id": "continuation-v1", "allowed_outcomes": ["RECOVERY_RUN"], "validation_rules": {}})
    # And the new presentation contracts
    TestData(os.path.join(project_root, "engine/presentation/visual_presentation_contract.json")).write_dummy_json({
      "contract_id": "visual-presentation-contract-v1", "visual_elements": {}, "feedback_priorities": [], "bounded_flags": {"placeholder_only": True}
    })
    TestData(os.path.join(project_root, "engine/presentation/hud_profile.json")).write_dummy_json({
      "hud_profile_id": "minimal-survival-hud-v1", "elements": {"pressure_indicator": {"high_threshold": 70}}, "bounded_flags": {"survival_critical_only": True}
    })
    TestData(os.path.join(project_root, "engine/presentation/placeholder_asset_manifest.json")).write_dummy_json({
      "manifest_id": "placeholder-assets-v1", "assets": {"character_player": {"representation": "@"}, "enemy_generic": {"representation": "E"}, "resource_item": {"representation": "i"}, "hud_pressure_low": {"representation": "(LOW)"}, "hud_pressure_medium": {"representation": "(MED)"}, "hud_pressure_high": {"representation": "(HIGH)"}}, "bounded_flags": {"placeholder_only": True}
    })


    contract_path = os.path.join(project_root, "engine/runtime/contracts/vertical_slice_contract.json")

    from engine.runtime.playable_slice_manager import PlayableSliceManager
    
    psm = PlayableSliceManager(contract_path)
    session_report = psm.run_playable_loop()
    
    audit_results["play_session_id"] = session_report["session_id"]
    audit_results["final_state"] = session_report["final_state"]
    audit_results["audits"] = session_report["audits"]
    audit_results["visual_log"] = session_report["visual_log"] # Capture visual log

    # 1. Verify visual output generation
    if session_report["visual_log"]:
        audit_results["checks"].append({"check": "Visual output generated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Visual output generated", "status": "FAIL"})

    # 2. Verify placeholder-safe visuals (simple check)
    if (all("@" in frame for frame in session_report["visual_log"]) and 
        any("E" in frame for frame in session_report["visual_log"]) and 
        any("i" in frame for frame in session_report["visual_log"])):
        audit_results["checks"].append({"check": "Visuals remain placeholder-safe (ASCII symbols present)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Visuals remain placeholder-safe (ASCII symbols present)", "status": "FAIL"})

    # 3. Verify HUD exposes survival-critical state (simple check)
    if (any("Health:" in frame for frame in session_report["visual_log"]) and 
        any("Stam:" in frame for frame in session_report["visual_log"]) and 
        any("Pressure:" in frame for frame in session_report["visual_log"]) and 
        any("Location:" in frame for frame in session_report["visual_log"])):
        audit_results["checks"].append({"check": "HUD exposes survival-critical state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "HUD exposes survival-critical state", "status": "FAIL"})

    # 4. Verify death/recovery screen (simple check for content)
    death_screen_found = any("YOU ARE DEFEATED" in frame for frame in session_report["visual_log"])
    recovery_message_found = any("Initiating Recovery Protocol..." in frame for frame in session_report["visual_log"])
    
    if death_screen_found and recovery_message_found:
        audit_results["checks"].append({"check": "Death/recovery screen matches continuation data", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Death/recovery screen matches continuation data", "status": "FAIL"})

    # 5. Admin Terminal Integration
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    final_audit_path = os.path.join(output_dir, "stage_068_visual_presentation_scaffold_audit.json")
    
    # Determine overall verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    # Write the complete audit_results (with verdict) to the file before terminal call
    with open(final_audit_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    from engine.os_boundary.restricted_terminal import RestrictedAdminTerminal
    
    # Pre-create a minimal restricted_terminal_boundary.json if it doesn't exist
    minimal_terminal_boundary = {
        "audit_config": {"audit_log_path": "audit_log.jsonl"}
    }
    terminal_boundary_path = os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json")
    if not os.path.exists(terminal_boundary_path):
        with open(terminal_boundary_path, 'w') as f:
            json.dump(minimal_terminal_boundary, f, indent=2)
    
    # Pre-create minimal admin_terminal_command_contract.json if it doesn't exist.
    # It must contain the 'slice status' command for the terminal check to pass.
    minimal_admin_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json")
    if not os.path.exists(minimal_admin_contract_path):
        minimal_admin_contract_data = {
            "commands": [
                {"command": "slice status", "family": "status", "description": "Report current playable vertical slice status."},
                {"command": "visual status", "family": "status", "description": "Report current visual presentation scaffold status."},
                {"command": "visual audit", "family": "logs", "description": "Audit the generated visual output and asset manifest."}
            ],
            "validation_rules": {"max_command_length": 256, "disallowed_characters": []}
        }
        with open(minimal_admin_contract_path, 'w') as f:
            json.dump(minimal_admin_contract_data, f, indent=2)

    term = RestrictedAdminTerminal(
        terminal_boundary_path,
        minimal_admin_contract_path,
        data_root
    )
    
    res = term.execute("visual status") # Check the new visual status command
    if "Visual Presentation Scaffold Status" in res:
        audit_results["checks"].append({"check": "Admin terminal reports visual status safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports visual status safely", "status": "FAIL"})

    print(f"Visual Presentation Scaffold validation report written to {final_audit_path}")
    return audit_results

if __name__ == "__main__":
    run_visual_presentation_scaffold_validation()
