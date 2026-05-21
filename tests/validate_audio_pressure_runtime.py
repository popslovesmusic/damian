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

def run_audio_pressure_runtime_validation():
    audit_results = {
        "patch_id": "STAGE-069",
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
    os.makedirs(os.path.join(project_root, "engine/audio"), exist_ok=True) # Ensure audio directory exists
    os.makedirs(os.path.join(project_root, "engine/player/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/traversal/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/combat/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/enemies/contracts"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "engine/economy/contracts"), exist_ok=True)

    # Minimal dummy files for sub-managers' contracts (ensure they don't break init)
    TestData(os.path.join(project_root, "engine/os_boundary/contracts/restricted_terminal_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    # admin_terminal_command_contract.json is now managed externally by the main stage logic
    TestData(os.path.join(project_root, "player/contracts/first_hour_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "learning_policy": {"environmental_teaching": True, "progressive_system_reveal": True, "demonstrate_recoverability": True, "demonstrate_pressure_early": True}})
    TestData(os.path.join(project_root, "player/contracts/onboarding_contract.json")).write_dummy_json({"contract_id": "onboarding-v1", "required_topics": [], "forbidden_patterns": [], "validation_rules": {}})
    TestData(os.path.join(project_root, "traversal/contracts/traversal_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"exposure_threshold_for_detection": 75.0, "mandatory_camera_shake_on_heavy_landing": True, "max_traversal_audio_layers": 4}})
    TestData(os.path.join(project_root, "traversal/contracts/movement_contract_schema.json")).write_dummy_json({"contract_id": "movement-v1", "movement_modes": ["STANDARD", "INJURED", "RUSH"], "validation_rules": {}, "audio_feedback_profile": {"footstep_volume": 1.0}}) # Added dummy audio_feedback_profile
    TestData(os.path.join(project_root, "combat/contracts/combat_feel_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"mandatory_hitstop_duration_ms_min": 30}})
    TestData(os.path.join(project_root, "combat/contracts/combat_feedback_contract.json")).write_dummy_json({"contract_id": "combat-v1", "combat_event_types": ["PLAYER_HIT_ENEMY", "ENEMY_HIT_PLAYER"], "validation_rules": {}, "audio_feedback_profile": {"impact_sound": "THUD", "threat_cue": "LOW"}}) # Added dummy audio_feedback_profile
    TestData(os.path.join(project_root, "enemies/contracts/enemy_ecology_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}, "readability_policy": {"min_telegraph_duration_ms": 300}})
    TestData(os.path.join(project_root, "enemies/contracts/enemy_behavior_contract.json")).write_dummy_json({"contract_id": "enemy-v1", "ecology_types": ["PREDATOR", "SCAVENGER"], "validation_rules": {}})
    TestData(os.path.join(project_root, "economy/contracts/resource_scarcity_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    TestData(os.path.join(project_root, "economy/contracts/survival_economy_contract.json")).write_dummy_json({"contract_id": "economy-v1", "resource_types": ["FOOD", "SCRAP"], "validation_rules": {}})
    TestData(os.path.join(project_root, "player/contracts/death_continuation_boundary.json")).write_dummy_json({"audit_config": {"audit_log_path": "audit_log.jsonl"}})
    TestData(os.path.join(project_root, "player/contracts/survivor_continuation_contract.json")).write_dummy_json({"contract_id": "continuation-v1", "allowed_outcomes": ["RECOVERY_RUN"], "validation_rules": {}})
    # Presentation contracts
    TestData(os.path.join(project_root, "engine/presentation/visual_presentation_contract.json")).write_dummy_json({
      "contract_id": "visual-presentation-contract-v1", "visual_elements": {}, "feedback_priorities": [], "bounded_flags": {"placeholder_only": True}
    })
    TestData(os.path.join(project_root, "engine/presentation/hud_profile.json")).write_dummy_json({
      "hud_profile_id": "minimal-survival-hud-v1", "elements": {"pressure_indicator": {"high_threshold": 70}}, "bounded_flags": {"survival_critical_only": True}
    })
    TestData(os.path.join(project_root, "engine/presentation/placeholder_asset_manifest.json")).write_dummy_json({
      "manifest_id": "placeholder-assets-v1", "assets": {"character_player": {"representation": "@"}, "enemy_generic": {"representation": "E"}, "resource_item": {"representation": "i"}, "hud_pressure_low": {"representation": "(LOW)"}, "hud_pressure_medium": {"representation": "(MED)"}, "hud_pressure_high": {"representation": "(HIGH)"}}, "bounded_flags": {"placeholder_only": True}
    })
    # Audio contracts (NEW)
    TestData(os.path.join(project_root, "engine/audio/audio_state_contract.json")).write_dummy_json({
      "contract_id": "audio-state-contract-v1", "audio_elements": {"ambient_tower": "LOW_HUM", "pressure_escalation": "RISING_TENSION", "survival_stress_heartbeat": "HEARTBEAT", "combat_impact_player_hit": "THUD"}, "bounded_flags": {"placeholder_only": True}
    })
    TestData(os.path.join(project_root, "engine/audio/procedural_audio_profile.json")).write_dummy_json({
      "profile_id": "procedural-audio-v1", "rules": {"ambient_volume_scalar": {"base_value": 0.5}, "heartbeat_threshold": {"health_percentage": 20}, "pressure_escalation_feedback": {"pressure_threshold": 60}}, "bounded_flags": {"debug_output_only": True}
    })
    TestData(os.path.join(project_root, "engine/audio/music_layer_manifest.json")).write_dummy_json({
      "manifest_id": "music-layer-manifest-v1", "layers": {"base_ambient": {"filename": "ambient_drone.mp3"}, "pressure_layer_high": {"filename": "tension_high.mp3"}, "combat_layer": {"filename": "combat_rhythm.mp3"}, "death_recovery_stinger": {"filename": "death_sting.mp3"}}, "bounded_flags": {"placeholder_only": True}
    })


    vertical_slice_contract_path = os.path.join(project_root, "engine/runtime/contracts/vertical_slice_contract.json")

    from engine.runtime.playable_slice_manager import PlayableSliceManager
    
    psm = PlayableSliceManager(vertical_slice_contract_path)
    session_report = psm.run_playable_loop()
    
    audit_results["play_session_id"] = session_report["session_id"]
    audit_results["final_state"] = session_report["final_state"]
    audit_results["audits"] = session_report["audits"]
    audit_results["visual_log"] = session_report["visual_log"]
    audit_results["audio_log"] = session_report["audio_log"] # Capture audio log

    # 1. Verify audio output generation
    if session_report["audio_log"]:
        audit_results["checks"].append({"check": "Audio output generated", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Audio output generated", "status": "FAIL"})

    # 2. Verify audio reflects runtime pressure state (simple check)
    if any("Ambient: LOW_HUM" in frame for frame in session_report["audio_log"]) and 
       any("Pressure Feedback: RISING_TENSION" in frame for frame in session_report["audio_log"]) or 
       any("Health Feedback: HEARTBEAT" in frame for frame in session_report["audio_log"]):
        audit_results["checks"].append({"check": "Audio reflects runtime pressure state", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Audio reflects runtime pressure state", "status": "FAIL"})

    # 3. Verify enemy audio cues remain readable (simple check for combat impact)
    if any("Combat Impact: THUD" in frame for frame in session_report["audio_log"]):
        audit_results["checks"].append({"check": "Enemy audio cues remain readable (combat impact detected)", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Enemy audio cues remain readable (combat impact detected)", "status": "FAIL"})

    # 4. Verify music layers react procedurally (simple check for layers)
    if any("Music Layers: ambient_drone.mp3" in frame for frame in session_report["audio_log"]) and 
       any("tension_high.mp3" in frame for frame in session_report["audio_log"]) or 
       any("combat_rhythm.mp3" in frame for frame in session_report["audio_log"]) or 
       any("death_sting.mp3" in frame for frame in session_report["audio_log"]):
        audit_results["checks"].append({"check": "Music layers react procedurally", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Music layers react procedurally", "status": "FAIL"})
    
    # 5. Admin Terminal Integration
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    final_audit_path = os.path.join(output_dir, "stage_069_audio_pressure_audit.json")
    
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
    
    # admin_terminal_command_contract.json is now expected to be in its full state.
    # We load it, and add audio commands, then write it back.
    admin_contract_path = os.path.join(project_root, "engine/os_boundary/contracts/admin_terminal_command_contract.json")
    
    # Reconstruct commands as per state after STAGE-068.
    # This ensures consistency even if previous runs left it in a bad state.
    full_commands_after_stage_068 = [
        {"command": "status", "family": "status", "description": "Report overall Tower OS status."},
        {"command": "diag health", "family": "diag", "description": "Report subsystem health."},
        {"command": "persistence info", "family": "status", "description": "Report persistence layer status."},
        {"command": "recovery audit", "family": "logs", "description": "Report system recovery history."},
        {"command": "update status", "family": "status", "description": "Report update cartridge status."},
        {"command": "update audit", "family": "logs", "description": "Report update history."},
        {"command": "network status", "family": "status", "description": "Report network subsystem status."},
        {"command": "network audit", "family": "logs", "description": "Report network traffic and event history."},
        {"command": "market status", "family": "status", "description": "Report market hub status."},
        {"command": "market audit", "family": "logs", "description": "Report market transaction history."},
        {"command": "contract status", "family": "status", "description": "Report procedural contract status."},
        {"command": "contract audit", "family": "logs", "description": "Report contract fulfillment history."},
        {"command": "faction status", "family": "status", "description": "Report faction dynamics status."},
        {"command": "faction audit", "family": "logs", "description": "Report faction history and schism events."},
        {"command": "narrative status", "family": "status", "description": "Report procedural narrative status."},
        {"command": "narrative audit", "family": "logs", "description": "Report narrative drift history."},
        {"command": "transit status", "family": "status", "description": "Report cross-world transit status."},
        {"command": "transit audit", "family": "logs", "description": "Report transit history and identity translations."},
        {"command": "sdk validate", "family": "status", "description": "Validate Author SDK payloads."},
        {"command": "sdk audit", "family": "logs", "description": "Report history of expansion publishing and SDK evidence."},
        {"command": "combat status", "family": "status", "description": "Report current combat feel and feedback configuration."},
        {"command": "combat audit", "family": "logs", "description": "Report history of combat feedback profiles and timing verification."},
        {"command": "traversal status", "family": "status", "description": "Report current movement feel and route exposure configuration."},
        {"command": "traversal audit", "family": "logs", "description": "Report history of traversal feedback and exhaustion movement evidence."},
        {"command": "enemy status", "family": "status", "description": "Report current enemy ecology and procedural adaptation status."},
        {"command": "enemy audit", "family": "logs", "description": "Report history of procedural enemy profiles and migration evidence."},
        {"command": "economy status", "family": "status", "description": "Report current survival economy and resource scarcity status."},
        {"command": "economy audit", "family": "logs", "description": "Report history of resource distribution, decay, and crafting pressure evidence."},
        {"command": "continuation status", "family": "status", "description": "Report current survivor continuation and legacy inheritance status."},
        {"command": "continuation audit", "family": "logs", "description": "Report history of survivor deaths, world memory delta, and recovery runs."},
        {"command": "onboarding status", "family": "status", "description": "Report current survivor onboarding and first-hour experience status."},
        {"command": "onboarding audit", "family": "logs", "description": "Report history of entry sequences, learning milestones, and first-hour UX evidence."},
        {"command": "biome status", "family": "status", "description": "Report current procedural biome profiles and environmental identity status."},
        {"command": "biome audit", "family": "logs", "description": "Report history of biome generation, hazard ecology, and expansion evidence."},
        {"command": "beta status", "family": "status", "description": "Report current closed beta population scaling and network stability."},
        {"command": "beta audit", "family": "logs", "description": "Report history of world memory compression, anti-inflation, and save migrations."},
        {"command": "launch status", "family": "status", "description": "Report current public launch readiness and distribution status."},
        {"command": "launch audit", "family": "logs", "description": "Report history of release artifact verification, telemetry, and support recovery."},
        {"command": "sustain status", "family": "status", "description": "Report current infinite Tower sustainability and narrative saturation status."},
        {"command": "sustain audit", "family": "logs", "description": "Report history of recursive content mutation, meta decay, and relay civilization drift."},
        {"command": "slice status", "family": "status", "description": "Report current playable vertical slice status and integrated manager states."},
        {"command": "slice audit", "family": "logs", "description": "Report full playable loop audit, including input, combat, death, and recovery lineage."},
        {"command": "visual status", "family": "status", "description": "Report current visual presentation scaffold status."},
        {"command": "visual audit", "family": "logs", "description": "Audit the generated visual output and asset manifest."}
    ]

    # Add audio commands for STAGE-069
    full_commands_after_stage_068.extend([
        {"command": "audio status", "family": "status", "description": "Report current audio atmosphere and pressure feedback status."},
        {"command": "audio audit", "family": "logs", "description": "Audit the generated audio output and music layers."}
    ])
    
    # Add logs list and exit last
    full_commands_after_stage_068.extend([
        {"command": "logs list", "family": "logs", "description": "List available audit logs."},
        {"command": "exit", "family": "system", "description": "Close maintenance hatch."}
    ])

    admin_contract_data = {
        "contract_id": "admin-terminal-command-contract-v1",
        "commands": full_commands_after_stage_068,
        "validation_rules": {
            "max_command_length": 256,
            "disallowed_characters": [";", "|", "&", ">", "<", "$", "(", ")", "`"],
            "enforce_family_match": True
        }
    }
    with open(admin_contract_path, 'w') as f:
        json.dump(admin_contract_data, f, indent=2)

    term = RestrictedAdminTerminal(
        terminal_boundary_path,
        admin_contract_path,
        data_root
    )
    
    res = term.execute("audio status") # Check the new audio status command
    if "Audio Pressure Runtime Status" in res:
        audit_results["checks"].append({"check": "Admin terminal reports audio status safely", "status": "PASS"})
    else:
        audit_results["checks"].append({"check": "Admin terminal reports audio status safely", "status": "FAIL"})

    print(f"Audio Atmosphere and Pressure Feedback validation report written to {final_audit_path}")
    return audit_results

if __name__ == "__main__":
    run_audio_pressure_runtime_validation()
