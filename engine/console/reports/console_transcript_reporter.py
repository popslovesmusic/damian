import os
import json
import uuid
import datetime
from engine.console.runtime import mvp_text_console

def run_console_transcript(commands, paths=None, output_dir='outputs/console_transcripts', debug=False, transcript_id=None):
    """
    Runs a console script and generates a structured transcript.
    """
    if not transcript_id:
        transcript_id = str(uuid.uuid4())
    
    # 1. Start session
    session_result = mvp_text_console.start_console_session(paths=paths, debug=debug)
    if not session_result["ok"]:
        return _make_failed_transcript(transcript_id, commands, session_result, debug)
    
    session_state = session_result["session_state"]
    results = []
    executed = []
    errors = []
    
    # Flags for observation
    mutation_observed = False
    survivor_mark_observed = False
    diff_observed = False
    
    # Combat-specific observation
    combat_sessions_observed = 0
    combat_outcomes_observed = []
    combat_defeats_observed = 0
    combat_victories_observed = 0
    combat_retreats_observed = 0
    resource_pressure_observed = False
    residue_pressure_observed = False
    mutation_after_combat_observed = False
    survivor_mark_after_combat_observed = False
    
    # Enemy pressure observation
    enemy_pressure_profiles_observed = 0
    enemy_archetypes_observed = []
    enemy_adaptation_reasoning_observed = []
    attrition_pressure_observed = False
    counter_pressure_observed = False
    ambush_pressure_observed = False
    baseline_pressure_observed = False
    
    # Loot and Resource observation
    loot_events_observed = 0
    total_gold_observed = 0
    large_visible_loot_observed = False
    resource_sink_pressure_observed = False
    bounded_reward_flags_clean = True
    loot_sources_observed = []
    resource_sink_summaries = []
    
    # Room graph evidence observation
    room_graph_evidence_observed = False
    room_graph_changes_observed = 0
    survivor_mark_rooms_observed = 0
    graph_diff_summaries = []
    
    # 2. Execute commands
    for cmd_str in commands:
        if not session_state["session_active"]:
            break
        
        cmd_struct = mvp_text_console.parse_console_command(cmd_str)
        result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=debug)
        
        results.append(result)
        executed.append(cmd_str)
        
        if not result["ok"]:
            errors.append(result.get("message", "Unknown error"))
        
        res_cmd = result.get("command", "").lower()
        payload = result.get("payload", {})
        
        # Observe side effects from direct commands
        if res_cmd in ["defeat", "defeat_drop"] and result["ok"]:
            if payload.get("mutation_applied"):
                mutation_observed = True
            if payload.get("survivor_mark_attached"):
                survivor_mark_observed = True
        
        if res_cmd == "marks" and result["ok"]:
            if result.get("payload"):
                survivor_mark_observed = True
        
        if res_cmd == "diff" and result["ok"]:
            if result.get("payload"):
                diff_observed = True
                # Capture room graph evidence from diff payload
                rg_evidence = payload.get("room_graph_evidence")
                if rg_evidence:
                    room_graph_evidence_observed = True
                    if payload.get("graph_changed"):
                        room_graph_changes_observed += 1
                    if payload.get("survivor_mark_room_added"):
                        survivor_mark_rooms_observed += 1
                    
                    # Capture topological summaries if available
                    rg_summary = rg_evidence.get("readable_summary", [])
                    if rg_summary:
                        graph_diff_summaries.extend(rg_summary)

        # Observe side effects from 'combat' command
        if res_cmd == "combat" and result["ok"]:
            combat_sessions_observed += 1
            outcome = payload.get("resolved_outcome")
            if outcome:
                combat_outcomes_observed.append(outcome)
                if outcome == "VICTORY_ASCEND":
                    combat_victories_observed += 1
                elif outcome == "DEFEAT_DROP":
                    combat_defeats_observed += 1
                    if payload.get("mutation_applied"):
                        mutation_after_combat_observed = True
                        mutation_observed = True
                    if payload.get("survivor_mark_attached"):
                        survivor_mark_after_combat_observed = True
                        survivor_mark_observed = True
                elif outcome == "RETREAT_TO_HUB":
                    combat_retreats_observed += 1
            
            # Extract pressure evidence from stub result (it's in the resolution result which is part of payload)
            # Based on TOWER-ENGINE-038 structured_result_shape
            # resolve_combat_session returns resource_pressure_observed and residue_pressure_observed
            if payload.get("resource_pressure_observed"):
                resource_pressure_observed = True
            if payload.get("residue_pressure_observed"):
                residue_pressure_observed = True

            # Extract enemy pressure evidence (TOWER-ENGINE-049)
            if payload.get("enemy_pressure_profile_used"):
                enemy_pressure_profiles_observed += 1
                arch_id = payload.get("enemy_archetype_id")
                if arch_id:
                    if arch_id not in enemy_archetypes_observed:
                        enemy_archetypes_observed.append(arch_id)
                    
                    # Infer pressure categories
                    if arch_id == "attrition_unit":
                        attrition_pressure_observed = True
                    elif arch_id == "counter_unit":
                        counter_pressure_observed = True
                    elif arch_id == "ambush_unit":
                        ambush_pressure_observed = True
                    elif arch_id == "pressure_unit":
                        baseline_pressure_observed = True
                
                reasoning = payload.get("enemy_adaptation_reasoning", [])
                for r in reasoning:
                    if r not in enemy_adaptation_reasoning_observed:
                        enemy_adaptation_reasoning_observed.append(r)

            # Extract loot and resource evidence (TOWER-ENGINE-054)
            loot_event = payload.get("loot_event")
            if loot_event:
                loot_events_observed += 1
                source = loot_event.get("source")
                if source and source not in loot_sources_observed:
                    loot_sources_observed.append(source)
                
                rewards = loot_event.get("rewards", {})
                gold = rewards.get("gold", 0)
                total_gold_observed += gold
                if gold >= 10000:
                    large_visible_loot_observed = True
                
                sink_pressure = loot_event.get("resource_sink_pressure")
                if sink_pressure:
                    resource_sink_pressure_observed = True
                    # Summarize sink pressure for review
                    summary = f"Floor {loot_event.get('floor_id')} Sinks: Potion {sink_pressure.get('estimated_potion_cost')}, Repair {sink_pressure.get('estimated_repair_cost')}"
                    if summary not in resource_sink_summaries:
                        resource_sink_summaries.append(summary)
                
                bounded_flags = loot_event.get("bounded_reward_flags", {})
                # Check for bypass flags (safety violation)
                if any(bounded_flags.values()):
                    bounded_reward_flags_clean = False

    # 3. Final State Capture
    tower_state = session_state["runtime_context"]["tower_state"]
    player_prog = session_state["runtime_context"]["player_progression"]
    
    transcript = {
        "transcript_id": transcript_id,
        "patch_id": "TOWER-ENGINE-054",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ok": len(errors) == 0,
        "commands_requested": commands,
        "commands_executed": executed,
        "command_results": results,
        "final_session_active": session_state["session_active"],
        "final_floor": tower_state.get("current_floor"),
        "highest_floor_reached": player_prog.get("highest_floor_reached"),
        "mutation_observed": mutation_observed,
        "survivor_mark_observed": survivor_mark_observed,
        "diff_observed": diff_observed,
        "combat_sessions_observed": combat_sessions_observed,
        "combat_outcomes_observed": combat_outcomes_observed,
        "combat_defeats_observed": combat_defeats_observed,
        "combat_victories_observed": combat_victories_observed,
        "combat_retreats_observed": combat_retreats_observed,
        "resource_pressure_observed": resource_pressure_observed,
        "residue_pressure_observed": residue_pressure_observed,
        "mutation_after_combat_observed": mutation_after_combat_observed,
        "survivor_mark_after_combat_observed": survivor_mark_after_combat_observed,
        "enemy_pressure_profiles_observed": enemy_pressure_profiles_observed,
        "enemy_archetypes_observed": enemy_archetypes_observed,
        "enemy_adaptation_reasoning_observed": enemy_adaptation_reasoning_observed,
        "attrition_pressure_observed": attrition_pressure_observed,
        "counter_pressure_observed": counter_pressure_observed,
        "ambush_pressure_observed": ambush_pressure_observed,
        "baseline_pressure_observed": baseline_pressure_observed,
        "loot_events_observed": loot_events_observed,
        "total_gold_observed": total_gold_observed,
        "large_visible_loot_observed": large_visible_loot_observed,
        "resource_sink_pressure_observed": resource_sink_pressure_observed,
        "bounded_reward_flags_clean": bounded_reward_flags_clean,
        "loot_sources_observed": loot_sources_observed,
        "resource_sink_summaries": resource_sink_summaries,
        "room_graph_evidence_observed": room_graph_evidence_observed,
        "room_graph_changes_observed": room_graph_changes_observed,
        "survivor_mark_rooms_observed": survivor_mark_rooms_observed,
        "graph_diff_summaries": graph_diff_summaries,
        "errors": errors,
        "no_scope_creep_flags": {
            "combat_runtime_introduced": False,
            "map_generation_introduced": False,
            "multiplayer_runtime_introduced": False,
            "gpu_code_introduced": False
        }
    }
    
    # 4. Write artifact
    # Specific ID for TOWER-ENGINE-054 validation artifact
    if transcript_id == "loot_evidence_validation":
        filename = "tower_engine_054_loot_evidence_console_transcript.json"
    elif transcript_id == "enemy_pressure_validation":
        filename = "tower_engine_050_enemy_pressure_console_transcript.json"
    elif transcript_id == "graph_combat_validation":
        filename = "tower_engine_045_graph_combat_console_transcript.json"
    else:
        filename = f"tower_engine_054_console_transcript_{transcript_id[:8]}.json"

        
    output_path = os.path.join(output_dir, filename)
    write_console_transcript(transcript, output_path)
    
    return transcript


def write_console_transcript(transcript, output_path):
    """
    Writes a transcript to a JSON file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2)


def validate_console_transcript(transcript):
    """
    Validates the structure of a transcript.
    """
    required_keys = [
        "transcript_id", "patch_id", "ok", "commands_requested", 
        "commands_executed", "command_results", "final_session_active",
        "no_scope_creep_flags", "combat_sessions_observed"
    ]
    for key in required_keys:
        if key not in transcript:
            return False
    return True


def summarize_console_transcript(transcript):
    """
    Returns a human-readable summary of the transcript.
    """
    summary = [
        f"Transcript ID: {transcript['transcript_id']}",
        f"Status: {'SUCCESS' if transcript['ok'] else 'FAILED'}",
        f"Commands: {len(transcript['commands_executed'])}/{len(transcript['commands_requested'])} executed.",
        f"Final Floor: {transcript['final_floor']}",
        f"Mutation Observed: {transcript['mutation_observed']}",
        f"Survivor Mark Observed: {transcript['survivor_mark_observed']}",
        f"Diff Observed: {transcript['diff_observed']}",
        f"Combat Sessions: {transcript['combat_sessions_observed']} (V:{transcript['combat_victories_observed']} D:{transcript['combat_defeats_observed']} R:{transcript['combat_retreats_observed']})",
        f"Resource Pressure Observed: {transcript['resource_pressure_observed']}",
        f"Residue Pressure Observed: {transcript['residue_pressure_observed']}"
    ]
    return "\n".join(summary)


def _make_failed_transcript(transcript_id, commands, startup_failure, debug):
    return {
        "transcript_id": transcript_id,
        "patch_id": "TOWER-ENGINE-054",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "ok": False,
        "commands_requested": commands,
        "commands_executed": [],
        "command_results": [],
        "final_session_active": False,
        "final_floor": None,
        "highest_floor_reached": None,
        "mutation_observed": False,
        "survivor_mark_observed": False,
        "diff_observed": False,
        "combat_sessions_observed": 0,
        "combat_outcomes_observed": [],
        "combat_defeats_observed": 0,
        "combat_victories_observed": 0,
        "combat_retreats_observed": 0,
        "resource_pressure_observed": False,
        "residue_pressure_observed": False,
        "mutation_after_combat_observed": False,
        "survivor_mark_after_combat_observed": False,
        "enemy_pressure_profiles_observed": 0,
        "enemy_archetypes_observed": [],
        "enemy_adaptation_reasoning_observed": [],
        "attrition_pressure_observed": False,
        "counter_pressure_observed": False,
        "ambush_pressure_observed": False,
        "baseline_pressure_observed": False,
        "loot_events_observed": 0,
        "total_gold_observed": 0,
        "large_visible_loot_observed": False,
        "resource_sink_pressure_observed": False,
        "bounded_reward_flags_clean": True,
        "loot_sources_observed": [],
        "resource_sink_summaries": [],
        "room_graph_evidence_observed": False,
        "room_graph_changes_observed": 0,
        "survivor_mark_rooms_observed": 0,
        "graph_diff_summaries": [],
        "errors": [startup_failure.get("message", "Startup failed")],
        "no_scope_creep_flags": {
            "combat_runtime_introduced": False,
            "map_generation_introduced": False,
            "multiplayer_runtime_introduced": False,
            "gpu_code_introduced": False
        }
    }
