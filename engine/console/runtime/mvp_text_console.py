import os
import json
import sys

# Import existing MVP systems
try:
    from engine.core.orchestrator import mvp_startup_orchestrator
    from engine.prototype.runtime import mvp_outcome_pipeline
    from engine.easter_eggs.runtime import mvp_survivor_mark_system
    from engine.reports.runtime import replay_floor_diff_reporter
    from engine.room_graph.runtime import room_graph_mutation_evidence
    from engine.floor_generation.runtime import floor_record_builder
    from engine.save.runtime import json_save_manager
    from engine.residue.runtime import mvp_residue_writer
    from engine.combat.runtime import mvp_combat_resolution_stub
    from engine.enemies.runtime import enemy_pressure_selector
    from engine.loot.runtime import mvp_loot_event_stub
    _dependencies_available = True
except ImportError as e:
    print(f"ERROR: Console runtime dependencies missing: {e}")
    _dependencies_available = False


def start_console_session(paths=None, debug=False):
    """
    Initializes a new console play session.
    """
    if not _dependencies_available:
        return {"ok": False, "message": "Dependencies unavailable."}

    startup_context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, debug=debug)
    if not startup_context["ok"]:
        return {"ok": False, "message": f"Startup failed: {startup_context.get('errors')}"}

    session_state = make_console_session_state(startup_context, debug=debug)
    return {"ok": True, "session_state": session_state}


def make_console_session_state(runtime_context, debug=False):
    """
    Creates the internal state for a console session.
    """
    return {
        "runtime_context": runtime_context,
        "session_active": True,
        "latest_diff": None,
        "debug_enabled": debug
    }


def parse_console_command(raw_command):
    """
    Parses a raw command string into a structured command.
    """
    parts = raw_command.strip().lower().split()
    if not parts:
        return {"command": "noop", "args": []}
    
    command = parts[0]
    args = parts[1:]
    return {"command": command, "args": args}


def execute_console_command(session_state, command_struct, debug=False):
    """
    Executes a structured console command.
    """
    command = command_struct["command"]
    args = command_struct["args"]
    
    if command == "status":
        return _handle_status(session_state, debug)
    elif command == "ascend":
        return _handle_outcome(session_state, "VICTORY_ASCEND", debug)
    elif command == "defeat":
        return _handle_outcome(session_state, "DEFEAT_DROP", debug)
    elif command == "retreat":
        return _handle_outcome(session_state, "RETREAT_TO_HUB", debug)
    elif command == "diff":
        return _handle_diff(session_state, debug)
    elif command == "marks":
        return _handle_marks(session_state, debug)
    elif command == "claim":
        if not args:
            return {"ok": False, "command": "claim", "message": "Missing survivor_mark_id.", "payload": None, "error": "MissingArgument"}
        return _handle_claim(session_state, args[0], debug)
    elif command == "combat":
        return _handle_combat(session_state, args, debug)
    elif command == "save":
        return _handle_save(session_state, debug)
    elif command == "quit":
        session_state["session_active"] = False
        return {"ok": True, "command": "quit", "message": "Session terminated.", "payload": None, "error": None}
    elif command == "help":
        return _handle_help()
    elif command == "noop":
        return {"ok": True, "command": "noop", "message": "", "payload": None, "error": None}
    else:
        return {"ok": False, "command": command, "message": f"Unknown command: {command}", "payload": None, "error": "UnknownCommand"}


def _handle_status(session_state, debug):
    tower_state = session_state["runtime_context"]["tower_state"]
    player_prog = session_state["runtime_context"]["player_progression"]
    
    current_floor = tower_state.get("current_floor", 1)
    highest_floor = player_prog.get("highest_floor_reached", 1)
    
    # Calculate residue count
    residue_count = 0
    for fm in tower_state.get("floor_memory", []):
        residue_count += len(fm.get("residue_history", []))
    
    # Get floor memory for current floor
    fm_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
    if fm_result["ok"]:
        fm = fm_result["payload"]
        mutation_count = len(fm.get("active_mutations", []))
        unclaimed_marks_count = len(fm.get("unclaimed_easter_eggs", []))
    else:
        mutation_count = 0
        unclaimed_marks_count = 0

    status_msg = (f"Floor: {current_floor} | Highest: {highest_floor} | "
                  f"Residues: {residue_count} | Mutations: {mutation_count} | "
                  f"Unclaimed Marks: {unclaimed_marks_count}")
    
    payload = {
        "current_floor": current_floor,
        "highest_floor": highest_floor,
        "residue_count": residue_count,
        "mutation_count": mutation_count,
        "unclaimed_marks_count": unclaimed_marks_count
    }
    
    return {"ok": True, "command": "status", "message": status_msg, "payload": payload, "error": None}


def _handle_outcome(session_state, outcome, debug):
    tower_state = session_state["runtime_context"]["tower_state"]
    
    # Snapshot floor memory and build record before for diffing if defeat
    before_fm = None
    floor_record = None
    if outcome == "DEFEAT_DROP":
        current_floor = tower_state.get("current_floor")
        fm_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
        if fm_result["ok"]:
            # Deep copy to avoid mutation affecting the 'before' snapshot
            before_fm = json.loads(json.dumps(fm_result["payload"]))
            # Also get floor record for graph building
            fr_result = floor_record_builder.make_floor_record(current_floor, debug=debug)
            if fr_result["ok"]:
                floor_record = fr_result["payload"]

    pipeline_result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(tower_state, outcome, debug=debug)
    
    if not pipeline_result["ok"]:
        return {"ok": False, "command": outcome.lower(), "message": f"Outcome resolution failed: {pipeline_result.get('error')}", "payload": None, "error": pipeline_result.get("error_type")}
    
    # Update state
    session_state["runtime_context"]["tower_state"] = pipeline_result["tower_state"]
    
    # If defeat, generate diff
    if outcome == "DEFEAT_DROP" and before_fm:
        target_floor_id = pipeline_result["current_floor"]
        prev_floor_id = pipeline_result["previous_floor"]
        
        if target_floor_id == prev_floor_id:
            after_fm = None
            for fm in pipeline_result["tower_state"]["floor_memory"]:
                if fm["floor_id"] == target_floor_id:
                    after_fm = fm
                    break
            
            if after_fm:
                diff_result = replay_floor_diff_reporter.make_replay_floor_diff_report(before_fm, after_fm, debug=debug)
                if diff_result["ok"]:
                    latest_diff = diff_result["payload"]
                    
                    # Integrate room graph evidence
                    if floor_record:
                        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(
                            floor_record, before_fm, after_fm, debug=debug
                        )
                        latest_diff["room_graph_evidence"] = evidence
                        latest_diff["graph_changed"] = evidence.get("graph_changed", False)
                        latest_diff["survivor_mark_room_added"] = evidence.get("survivor_mark_room_added", False)
                        if evidence.get("ok") and evidence.get("readable_summary"):
                            latest_diff["readable_summary"].extend(evidence["readable_summary"])
                    
                    session_state["latest_diff"] = latest_diff
        else:
            session_state["latest_diff"] = None 

    msg = f"Outcome {outcome} resolved. New floor: {pipeline_result['current_floor']}."
    return {"ok": True, "command": outcome.lower(), "message": msg, "payload": pipeline_result, "error": None}


def _handle_diff(session_state, debug):
    if not session_state["latest_diff"]:
        return {"ok": True, "command": "diff", "message": "No recent diff available.", "payload": None, "error": None}
    
    summary = session_state["latest_diff"].get("readable_summary", [])
    msg = "\n".join(summary) if summary else "No significant changes detected in latest diff."
    return {"ok": True, "command": "diff", "message": msg, "payload": session_state["latest_diff"], "error": None}


def _handle_marks(session_state, debug):
    tower_state = session_state["runtime_context"]["tower_state"]
    current_floor = tower_state.get("current_floor", 1)
    
    fm_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
    if not fm_result["ok"]:
        return {"ok": False, "command": "marks", "message": "Could not access floor memory.", "payload": None, "error": "FloorMemoryError"}
    
    fm = fm_result["payload"]
    marks_list = fm.get("unclaimed_easter_eggs", [])
    
    if not marks_list:
        return {"ok": True, "command": "marks", "message": "No unclaimed marks on this floor.", "payload": [], "error": None}
    
    msg = "Unclaimed marks: " + ", ".join(marks_list)
    return {"ok": True, "command": "marks", "message": msg, "payload": marks_list, "error": None}


def _handle_claim(session_state, mark_id, debug):
    tower_state = session_state["runtime_context"]["tower_state"]
    current_floor = tower_state.get("current_floor", 1)
    
    fm_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
    if not fm_result["ok"]:
        return {"ok": False, "command": "claim", "message": "Could not access floor memory.", "payload": None, "error": "FloorMemoryError"}
    
    fm = fm_result["payload"]
    
    # 1. Discover if needed
    if mark_id in fm.get("unclaimed_easter_eggs", []):
        discover_result = mvp_survivor_mark_system.discover_survivor_mark(fm, mark_id, debug=debug)
        if not discover_result["ok"]:
            return {"ok": False, "command": "claim", "message": f"Discovery failed: {discover_result.get('message')}", "payload": None, "error": discover_result.get("error_type")}
        fm = discover_result["payload"]

    # 2. Claim
    claim_result = mvp_survivor_mark_system.claim_survivor_mark(fm, mark_id, debug=debug)
    if not claim_result["ok"]:
        return {"ok": False, "command": "claim", "message": f"Claim failed: {claim_result.get('message')}", "payload": None, "error": claim_result.get("error_type")}
    
    # Reward is in payload
    reward = claim_result["payload"]
    msg = f"Mark {mark_id} claimed! Reward: {reward.get('type')} (Value: {reward.get('value')})."
    return {"ok": True, "command": "claim", "message": msg, "payload": reward, "error": None}


def _handle_combat(session_state, args, debug):
    if not _dependencies_available:
        return {"ok": False, "command": "combat", "message": "Combat dependencies missing.", "payload": None, "error": "DependencyError"}

    tower_state = session_state["runtime_context"]["tower_state"]
    
    # Defaults
    enemy_pressure = 0.25
    resource_usage = {"potions_used": 0, "repair_items_used": 0, "recovery_events": 0}
    player_health = 100.0
    
    variant = args[0] if args else "safe"
    if variant == "safe":
        enemy_pressure = 0.25
        player_health = 100.0
    elif variant == "dangerous":
        enemy_pressure = 0.95
        player_health = 20.0
    elif variant == "exhausted":
        enemy_pressure = 0.70
        resource_usage["potions_used"] = 30
        player_health = 50.0
    
    current_floor = tower_state.get("current_floor", 1)
    
    # Snapshot floor memory and build record before for diffing if defeat
    before_fm = None
    floor_record = None
    fm_result = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
    if fm_result["ok"]:
        before_fm = json.loads(json.dumps(fm_result["payload"]))
        fr_result = floor_record_builder.make_floor_record(current_floor, debug=debug)
        if fr_result["ok"]:
            floor_record = fr_result["payload"]

    # Select enemy pressure profile based on current floor memory
    arch_id = enemy_pressure_selector.select_enemy_archetype(before_fm, debug=debug)
    pressure_profile = enemy_pressure_selector.build_enemy_pressure_profile(arch_id, before_fm, debug=debug)

    # 1. Build session
    player_state = {"player_id": "console_player", "health": player_health}
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        current_floor, player_state, enemy_pressure_rating=enemy_pressure, 
        resource_usage=resource_usage, enemy_pressure_profile=pressure_profile, debug=debug
    )
    
    # 2. Resolve into pipeline
    resolution_result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, combat_session, debug=debug)
    
    if not resolution_result["ok"]:
        return {"ok": False, "command": "combat", "message": f"Combat resolution failed: {resolution_result.get('error')}", "payload": None, "error": "ResolutionError"}

    pipeline_result = resolution_result["pipeline_result"]
    resolved_outcome = resolution_result["resolved_outcome"]
    
    # 3. Generate Bounded Loot Event (TOWER-ENGINE-053)
    loot_res = mvp_loot_event_stub.make_combat_loot_event(current_floor, outcome=resolved_outcome, debug=debug)
    loot_event = loot_res["payload"] if loot_res["ok"] else None
    loot_summary = mvp_loot_event_stub.summarize_loot_event(loot_event) if loot_event else "Loot generation failed."

    # Update state
    session_state["runtime_context"]["tower_state"] = pipeline_result["tower_state"]
    
    # 4. Handle Diff for defeat
    if resolved_outcome == "DEFEAT_DROP" and before_fm:
        target_floor_id = pipeline_result["current_floor"]
        prev_floor_id = pipeline_result["previous_floor"]
        if target_floor_id == prev_floor_id:
            after_fm = next((fm for fm in pipeline_result["tower_state"]["floor_memory"] if fm["floor_id"] == target_floor_id), None)
            if after_fm:
                diff_res = replay_floor_diff_reporter.make_replay_floor_diff_report(before_fm, after_fm, debug=debug)
                if diff_res["ok"]:
                    latest_diff = diff_res["payload"]
                    
                    # Integrate room graph evidence
                    if floor_record:
                        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(
                            floor_record, before_fm, after_fm, debug=debug
                        )
                        latest_diff["room_graph_evidence"] = evidence
                        latest_diff["graph_changed"] = evidence.get("graph_changed", False)
                        latest_diff["survivor_mark_room_added"] = evidence.get("survivor_mark_room_added", False)
                        if evidence.get("ok") and evidence.get("readable_summary"):
                            latest_diff["readable_summary"].extend(evidence["readable_summary"])
                    
                    session_state["latest_diff"] = latest_diff
        else:
            session_state["latest_diff"] = None

    msg = f"Combat ({variant}) resolved to {resolved_outcome}. New floor: {pipeline_result['current_floor']}.\n{loot_summary}"
    
    payload = {
        "resolved_outcome": resolved_outcome,
        "combat_session": combat_session,
        "pipeline_result": pipeline_result,
        "mutation_applied": pipeline_result.get("mutation_applied", False),
        "survivor_mark_attached": pipeline_result.get("survivor_mark_attached", False),
        "resource_pressure_observed": resolution_result.get("resource_pressure_observed", False),
        "residue_pressure_observed": resolution_result.get("residue_pressure_observed", False),
        "enemy_pressure_profile": pressure_profile,
        "enemy_archetype_id": resolution_result.get("enemy_archetype_id"),
        "enemy_adaptation_reasoning": resolution_result.get("enemy_adaptation_reasoning", []),
        "enemy_pressure_profile_used": resolution_result.get("enemy_pressure_profile_used", False),
        "loot_event": loot_event,
        "loot_summary": loot_summary,
        "resource_sink_pressure": loot_event.get("resource_sink_pressure") if loot_event else None,
        "bounded_reward_flags": loot_event.get("bounded_reward_flags") if loot_event else None
    }
    
    return {"ok": True, "command": "combat", "message": msg, "payload": payload, "error": None}


def _handle_save(session_state, debug):
    runtime_context = session_state["runtime_context"]
    tower_state = runtime_context["tower_state"]
    
    # Get path from orchestrator defaults
    paths = mvp_startup_orchestrator.make_default_runtime_paths()
    save_path = paths["tower_state"]
    
    save_result = json_save_manager.save_json(save_path, tower_state, debug=debug)
    if not save_result["ok"]:
        return {"ok": False, "command": "save", "message": f"Save failed: {save_result.get('message')}", "payload": None, "error": "SaveError"}
    
    return {"ok": True, "command": "save", "message": f"Tower state saved to {save_path}.", "payload": {"path": save_path}, "error": None}


def _handle_help():
    commands = [
        "status   - Show current tower status.",
        "ascend   - Victory! Ascend to the next floor.",
        "defeat   - Defeat! Drop back and trigger mutation/marks.",
        "retreat  - Retreat to the Hub.",
        "diff     - Show changes from the latest defeat.",
        "marks    - List unclaimed survivor marks on current floor.",
        "claim ID - Claim a survivor mark by its ID.",
        "combat V - Resolve combat stub (safe|dangerous|exhausted).",
        "save     - Persist current progress.",
        "quit     - Exit the session.",
        "help     - Show this help message."
    ]
    msg = "Supported commands:\n" + "\n".join(commands)
    return {"ok": True, "command": "help", "message": msg, "payload": None, "error": None}


def run_console_script(commands, paths=None, debug=False):
    """
    Executes a sequence of commands and returns the results.
    """
    session_result = start_console_session(paths=paths, debug=debug)
    if not session_result["ok"]:
        return [session_result]
    
    session_state = session_result["session_state"]
    results = []
    
    for cmd_str in commands:
        if not session_state["session_active"]:
            break
        
        cmd_struct = parse_console_command(cmd_str)
        result = execute_console_command(session_state, cmd_struct, debug=debug)
        results.append(result)
        
    return results
