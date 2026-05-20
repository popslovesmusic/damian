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
    from engine.equipment.runtime import equipment_pressure_stub
    from engine.inventory.runtime import inventory_capacity_pressure
    from engine.equipment.repair import repair_runtime_stub
    from engine.traversal.runtime import traversal_pressure_stub
    from engine.room_graph.runtime import room_graph_builder
    from engine.room_graph.traversal import room_traversal_route_builder
    _dependencies_available = True
except ImportError as e:
    print(f"ERROR: Console runtime dependencies missing: {e}")
    _dependencies_available = False

# Path to example equipment for console stub
_PROJECT_ROOT_CON = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_EXAMPLE_LOADOUT_PATH = os.path.join(_PROJECT_ROOT_CON, "engine/equipment/contracts/example_equipment_loadout.json")


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
    # Initialize inventory if not present in context (TOWER-ENGINE-064)
    inventory_state = runtime_context.get("inventory_state")
    if not inventory_state:
        from engine.inventory.runtime import inventory_transaction_stub
        inventory_state = inventory_transaction_stub.make_default_inventory_state(debug=debug)

    # Initialize equipment loadout (TOWER-ENGINE-078)
    equipment_loadout = runtime_context.get("equipment_loadout")
    if not equipment_loadout and os.path.exists(_EXAMPLE_LOADOUT_PATH):
        try:
            with open(_EXAMPLE_LOADOUT_PATH, 'r') as f:
                equipment_loadout = json.load(f)
        except Exception as e:
            if debug:
                print(f"DEBUG: Failed to load example loadout in session state: {e}")

    return {
        "runtime_context": runtime_context,
        "inventory_state": inventory_state,
        "equipment_loadout": equipment_loadout,
        "last_inventory_transaction": None,
        "last_durability_events": [],
        "durability_pressure_observed": False,
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
    elif command == "advance":
        return _handle_traversal_command(session_state, "advance", debug)
    elif command == "escape":
        return _handle_traversal_command(session_state, "escape_attempt", debug)
    elif command == "potion":
        return _handle_potion(session_state, args, debug)
    elif command == "repair":
        return _handle_repair(session_state, args, debug)
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

    # Get capacity pressure summary (TOWER-ENGINE-072)
    inventory_state = session_state.get("inventory_state")
    cap_summary = None
    cap_p = 0.0
    if inventory_state:
        cap_summary = inventory_capacity_pressure.summarize_capacity_pressure(inventory_state, debug=debug)
        if cap_summary.get("ok"):
            cap_p = cap_summary.get("capacity_pressure", 0.0)

    # Derive traversal pressure inputs (TOWER-ENGINE-087)
    mut_p = min(1.0, mutation_count * 0.2)
    
    # Derive combat exposure from durability activity proxy
    comb_e = 0.5 if session_state.get("durability_pressure_observed") else 0.1
    
    # Derive repair burden from equipment loadout
    rep_b = 0.0
    equipment_loadout = session_state.get("equipment_loadout")
    if equipment_loadout:
        rep_b = equipment_loadout.get("aggregate_pressure", {}).get("repair_pressure", 0.0)

    # Calculate current traversal hazard
    from engine.traversal.runtime import traversal_pressure_stub
    pressure_inputs = {
        "capacity_pressure": cap_p,
        "mutation_pressure": mut_p,
        "combat_exposure": comb_e,
        "repair_burden": rep_b,
        "route_exposure": 0.2 # Baseline for status check
    }
    
    traversal_res = traversal_pressure_stub.make_traversal_event(
        player_id="console_player",
        source_floor_id=current_floor,
        destination_floor_id=current_floor + 1,
        traversal_type="advance",
        pressure_inputs=pressure_inputs,
        debug=debug
    )
    
    traversal_event = traversal_res.get("traversal_event") if traversal_res["ok"] else None

    status_msg = (f"Floor: {current_floor} | Highest: {highest_floor} | "
                  f"Residues: {residue_count} | Mutations: {mutation_count} | "
                  f"Unclaimed Marks: {unclaimed_marks_count}")
    
    if cap_summary and cap_summary.get("ok"):
        status_msg += f" | Capacity: {cap_summary.get('capacity_band')}"
        
    if traversal_event:
        status_msg += f" | Traversal Risk: {traversal_event.get('escape_risk'):.2f}"

    payload = {
        "current_floor": current_floor,
        "highest_floor": highest_floor,
        "residue_count": residue_count,
        "mutation_count": mutation_count,
        "unclaimed_marks_count": unclaimed_marks_count,
        "capacity_pressure_summary": cap_summary,
        "capacity_pressure": cap_p,
        "capacity_band": cap_summary.get("capacity_band") if cap_summary else None,
        "over_capacity": cap_summary.get("over_capacity", False) if cap_summary else False,
        "traversal_pressure_summary": traversal_res.get("summary"),
        "traversal_pressure": traversal_event.get("traversal_pressure", {}).get("total_pressure", 0.0) if traversal_event else None, # Wait, total_pressure is not in schema but derived.
        "escape_risk": traversal_event.get("escape_risk") if traversal_event else None,
        "route_exposure": traversal_event.get("route_exposure") if traversal_event else None,
        "traversal_pressure_inputs": {
            "capacity_pressure": cap_p,
            "mutation_pressure": mut_p,
            "combat_exposure": comb_e,
            "repair_burden": rep_b
        }
    }
    
    # Fix traversal_pressure field name to match schema-derived total
    if traversal_event:
        # Re-calculate or just use the weighted sum
        payload["traversal_pressure"] = traversal_pressure_stub.calculate_traversal_pressure(
            cap_p, mut_p, comb_e, rep_b, debug=debug
        )
    
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
        msg = pipeline_result.get("message")
        if not msg and "error" in pipeline_result:
            msg = pipeline_result["error"].get("message")
        return {"ok": False, "command": outcome.lower(), "message": f"Outcome resolution failed: {msg}", "payload": None, "error": pipeline_result.get("error_type")}
    
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

    # Load equipment loadout from session state (TOWER-ENGINE-078)
    equipment_loadout = session_state.get("equipment_loadout")

    # Build Room Graph Evidence for combat bias (TOWER-ENGINE-097)
    selected_route = None
    if floor_record:
        has_marks = len(before_fm.get("unclaimed_easter_eggs", [])) > 0 if before_fm else False
        graph_res = room_graph_builder.build_room_graph(floor_record, include_survivor_mark_room=has_marks, debug=debug)
        if graph_res["ok"]:
            room_graph = graph_res["payload"]
            routes_res = room_traversal_route_builder.build_routes_from_room_graph(room_graph, debug=debug)
            if routes_res["ok"]:
                # Pick a representative route (primary or pressure) for combat context
                selected_route = next((r for r in routes_res["routes"] if r["route_type"] in ["primary_route", "pressure_route"]), routes_res["routes"][0] if routes_res["routes"] else None)

    # Derive Traversal Pressure for combat bias (TOWER-ENGINE-090/097)
    mutation_count = len(before_fm.get("active_mutations", [])) if before_fm else 0
    cap_p_trav = inventory_capacity_pressure.calculate_capacity_pressure(session_state["inventory_state"], debug=debug) or 0.0
    mut_p_trav = min(1.0, mutation_count * 0.2)
    rep_b_trav = equipment_loadout.get("aggregate_pressure", {}).get("repair_pressure", 0.0) if equipment_loadout else 0.0
    
    route_exp_trav = selected_route.get("route_exposure", 0.3) if selected_route else 0.3
    
    traversal_pressure_summary = {
        "traversal_pressure": traversal_pressure_stub.calculate_traversal_pressure(
            cap_p_trav, mut_p_trav, 0.5, rep_b_trav, route_exposure=route_exp_trav, 
            environmental_profile=selected_route.get("environmental_profile") if selected_route else None, debug=debug
        ),
        "escape_risk": traversal_pressure_stub.calculate_escape_risk(0.5, route_exp_trav, escape_modifier=selected_route.get("escape_modifier", 0.0) if selected_route else 0.0, debug=debug),
        "route_exposure": route_exp_trav
    }

    # 1. Build session
    player_state = {"player_id": "console_player", "health": player_health}
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        current_floor, player_state, enemy_pressure_rating=enemy_pressure, 
        resource_usage=resource_usage, enemy_pressure_profile=pressure_profile,
        equipment_loadout=equipment_loadout, traversal_pressure_summary=traversal_pressure_summary, 
        selected_route=selected_route, debug=debug
    )
    
    # 2. Resolve into pipeline
    resolution_result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, combat_session, debug=debug)
    
    if not resolution_result["ok"]:
        return {"ok": False, "command": "combat", "message": f"Combat resolution failed: {resolution_result.get('error')}", "payload": None, "error": "ResolutionError"}

    # Update session state with durability results (TOWER-ENGINE-078)
    if resolution_result.get("updated_equipment_loadout"):
        session_state["equipment_loadout"] = resolution_result["updated_equipment_loadout"]
    session_state["last_durability_events"] = resolution_result.get("durability_events", [])
    session_state["durability_pressure_observed"] = resolution_result.get("durability_pressure_observed", False)

    pipeline_result = resolution_result["pipeline_result"]
    resolved_outcome = resolution_result["resolved_outcome"]
    
    # 3. Generate Bounded Loot Event (TOWER-ENGINE-053)
    loot_res = mvp_loot_event_stub.make_combat_loot_event(current_floor, outcome=resolved_outcome, debug=debug)
    loot_event = loot_res["payload"] if loot_res["ok"] else None
    loot_summary = mvp_loot_event_stub.summarize_loot_event(loot_event) if loot_event else "Loot generation failed."

    # 4. Apply Loot to Inventory (TOWER-ENGINE-064/065 integration)
    inventory_transaction = None
    cap_summary = None
    if loot_event:
        from engine.inventory.runtime import inventory_transaction_stub
        inv_res = inventory_transaction_stub.add_loot_to_inventory(session_state["inventory_state"], loot_event, debug=debug)
        if inv_res["ok"]:
            session_state["inventory_state"] = inv_res["inventory_state"]
        # In both success and safe-failure, we capture the transaction as evidence
        inventory_transaction = inv_res.get("transaction")
        cap_summary = inv_res.get("capacity_pressure_summary")
        session_state["last_inventory_transaction"] = inventory_transaction

    # Update state
    session_state["runtime_context"]["tower_state"] = pipeline_result["tower_state"]
    
    # 5. Handle Diff for defeat
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
        "bounded_reward_flags": loot_event.get("bounded_reward_flags") if loot_event else None,
        "equipment_loadout": session_state.get("equipment_loadout"),
        "equipment_pressure": resolution_result.get("equipment_pressure"),
        "equipment_pressure_used": resolution_result.get("equipment_pressure_used", False),
        "repair_pressure_observed": resolution_result.get("repair_pressure_observed", False),
        "equipment_residue_visibility_observed": resolution_result.get("equipment_residue_visibility_observed", False),
        "equipment_mutation_affinity_observed": resolution_result.get("equipment_mutation_affinity_observed", False),
        "inventory_transaction": inventory_transaction,
        "inventory_state_summary": inventory_transaction_stub.summarize_inventory_state(session_state["inventory_state"]) if inventory_transaction else None,
        "capacity_pressure_summary": cap_summary,
        "capacity_pressure": cap_summary.get("capacity_pressure") if cap_summary else None,
        "capacity_band": cap_summary.get("capacity_band") if cap_summary else None,
        "over_capacity": cap_summary.get("over_capacity", False) if cap_summary else False,
        "durability_decay_applied": resolution_result.get("durability_decay_applied", False),
        "durability_events": resolution_result.get("durability_events", []),
        "updated_equipment_loadout": resolution_result.get("updated_equipment_loadout"),
        "durability_pressure_observed": resolution_result.get("durability_pressure_observed", False)
    }
    
    return {"ok": True, "command": "combat", "message": msg, "payload": payload, "error": None}


def _handle_potion(session_state, args, debug):
    inventory_state = session_state.get("inventory_state")
    if not inventory_state:
         return {"ok": False, "command": "potion", "message": "Inventory state missing.", "payload": None, "error": "InventoryError"}

    qty = 1
    if args:
        try:
            qty = int(args[0])
            if qty < 1:
                raise ValueError("Quantity must be >= 1")
        except ValueError:
             return {"ok": False, "command": "potion", "message": "Invalid quantity. Must be integer >= 1.", "payload": None, "error": "InvalidArguments"}

    from engine.inventory.runtime import inventory_transaction_stub
    
    item_id = "ash_potion_small"
    res = inventory_transaction_stub.consume_inventory_item(inventory_state, item_id, quantity=qty, debug=debug)
    
    if res["ok"]:
        session_state["inventory_state"] = res["inventory_state"]
        msg = f"Consumed {qty} {item_id}."
    else:
        msg = f"Failed to consume {item_id}: {res['error']['message']}"
    
    session_state["last_inventory_transaction"] = res.get("transaction")
    cap_summary = res.get("capacity_pressure_summary")
        
    payload = {
        "inventory_transaction": res.get("transaction"),
        "inventory_summary": res.get("summary"),
        "consumable_used": res["ok"],
        "item_id": item_id,
        "quantity_requested": qty,
        "capacity_pressure_summary": cap_summary,
        "capacity_pressure": cap_summary.get("capacity_pressure") if cap_summary else None,
        "capacity_band": cap_summary.get("capacity_band") if cap_summary else None,
        "over_capacity": cap_summary.get("over_capacity", False) if cap_summary else False
    }
    
    return {"ok": res["ok"], "command": "potion", "message": msg, "payload": payload, "error": res.get("error")}


def _handle_repair(session_state, args, debug):
    inventory_state = session_state.get("inventory_state")
    if not inventory_state:
         return {"ok": False, "command": "repair", "message": "Inventory state missing.", "payload": None, "error": "InventoryError"}

    equipment_loadout = session_state.get("equipment_loadout")
    if not equipment_loadout:
         return {"ok": False, "command": "repair", "message": "No equipment loadout available to repair.", "payload": None, "error": "EquipmentError"}

    # Select first repairable item (TOWER-ENGINE-082)
    repairable_item = None
    item_index = -1
    for i, item in enumerate(equipment_loadout.get("equipped_items", [])):
        durability = item.get("durability", {})
        if durability.get("current", 0) < durability.get("maximum", 1):
            repairable_item = item
            item_index = i
            break
    
    if not repairable_item:
        return {"ok": True, "command": "repair", "message": "All equipment is at maximum durability.", "payload": {"repair_applied": False, "durability_restored": 0}, "error": None}

    qty = 1
    if args:
        try:
            qty = int(args[0])
            if qty < 1:
                raise ValueError("Quantity must be >= 1")
        except ValueError:
             return {"ok": False, "command": "repair", "message": "Invalid quantity. Must be integer >= 1.", "payload": None, "error": "InvalidArguments"}

    from engine.equipment.repair import repair_runtime_stub
    item_id = "repair_material_basic"
    
    # 2. Execute material repair
    res = repair_runtime_stub.apply_repair(repairable_item, inventory_state, material_quantity=qty, debug=debug)
    
    if res["ok"]:
        # Update session state (TOWER-ENGINE-082)
        session_state["inventory_state"] = res["inventory_state"]
        
        # Update the item in the loadout
        new_loadout = json.loads(json.dumps(equipment_loadout)) # Deep copy
        new_loadout["equipped_items"][item_index] = res["equipment_item"]
        
        # Recalculate aggregate pressure for the loadout
        from engine.equipment.runtime import equipment_pressure_stub
        new_loadout["aggregate_pressure"] = equipment_pressure_stub.calculate_aggregate_equipment_pressure(
            new_loadout["equipped_items"], debug=debug
        )
        session_state["equipment_loadout"] = new_loadout
        
        msg = res["summary"]
    else:
        msg = f"Repair failed: {res['error']['message']}"
    
    session_state["last_inventory_transaction"] = res.get("inventory_transaction")
    cap_summary = res.get("inventory_transaction", {}).get("capacity_pressure_summary") if res.get("inventory_transaction") else None
    if not cap_summary and res.get("inventory_state"):
        # Fallback to manual check if transaction didn't return it
        from engine.inventory.runtime import inventory_capacity_pressure
        cap_summary = inventory_capacity_pressure.summarize_capacity_pressure(session_state["inventory_state"], debug=debug)
        
    payload = {
        "repair_event": res.get("repair_event"),
        "inventory_transaction": res.get("inventory_transaction"),
        "updated_equipment_loadout": session_state.get("equipment_loadout"),
        "updated_inventory_state": session_state.get("inventory_state"),
        "repair_applied": res["ok"] and res.get("repair_event", {}).get("repair_applied", False),
        "item_id": item_id,
        "quantity_requested": qty,
        "durability_restored": res.get("repair_event", {}).get("durability_restored", 0.0) if res.get("repair_event") else 0.0,
        "durability_restored_flag": res["ok"] and res.get("repair_event", {}).get("durability_restored", 0) > 0,
        "capacity_pressure_summary": cap_summary,
        "capacity_pressure": cap_summary.get("capacity_pressure") if cap_summary else None,
        "capacity_band": cap_summary.get("capacity_band") if cap_summary else None,
        "over_capacity": cap_summary.get("over_capacity", False) if cap_summary else False
    }
    
    return {"ok": res["ok"], "command": "repair", "message": msg, "payload": payload, "error": res.get("error")}


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


def _handle_traversal_command(session_state, traversal_type, debug):
    """
    Handles bounded spatial movement (advance or escape) with room-route-aware pressure.
    """
    tower_state = session_state["runtime_context"]["tower_state"]
    current_floor = tower_state.get("current_floor", 1)
    
    # 1. Build or Load Room Graph Evidence (TOWER-ENGINE-095)
    fr_res = floor_record_builder.make_floor_record(current_floor, debug=debug)
    if not fr_res["ok"]:
        return {"ok": False, "command": traversal_type, "message": f"Floor record failed: {fr_res.get('message')}", "payload": None, "error": "FloorError"}
    
    # Check if we should include SM room (proxy: if marks exist in floor memory)
    fm_res = mvp_residue_writer.get_or_create_floor_memory(tower_state, current_floor, debug=debug)
    has_marks = len(fm_res["payload"].get("unclaimed_easter_eggs", [])) > 0 if fm_res["ok"] else False
    
    graph_res = room_graph_builder.build_room_graph(fr_res["payload"], include_survivor_mark_room=has_marks, debug=debug)
    if not graph_res["ok"]:
        return {"ok": False, "command": traversal_type, "message": f"Graph build failed: {graph_res.get('message')}", "payload": None, "error": "GraphError"}
    
    room_graph = graph_res["payload"]
    
    # 2. Build Room Traversal Routes
    routes_res = room_traversal_route_builder.build_routes_from_room_graph(room_graph, debug=debug)
    if not routes_res["ok"]:
        return {"ok": False, "command": traversal_type, "message": f"Route building failed: {routes_res.get('message')}", "payload": None, "error": "RouteError"}
    
    room_routes = routes_res["routes"]
    
    # 3. Select Appropriate Route
    selected_route = None
    if traversal_type == "advance":
        # Prefer primary or pressure routes for advancing
        selected_route = next((r for r in room_routes if r["route_type"] in ["primary_route", "pressure_route"]), None)
    else:
        # Prefer escape or recovery routes for retreating
        selected_route = next((r for r in room_routes if r["route_type"] in ["escape_route", "recovery_route"]), room_routes[0] if room_routes else None)

    # 4. Derive Pressure Inputs
    cap_p = 0.0
    inventory_state = session_state.get("inventory_state")
    if inventory_state:
        cap_p = inventory_capacity_pressure.calculate_capacity_pressure(inventory_state, debug=debug) or 0.0

    mutation_count = len(fm_res["payload"].get("active_mutations", [])) if fm_res["ok"] else 0
    mut_p = min(1.0, mutation_count * 0.2)
    comb_e = 0.5 if session_state.get("durability_pressure_observed") else 0.1

    rep_b = 0.0
    loadout = session_state.get("equipment_loadout")
    if loadout:
        rep_b = loadout.get("aggregate_pressure", {}).get("repair_pressure", 0.0)

    # 5. Calculate Route-Aware Traversal Hazard
    from engine.traversal.runtime import traversal_pressure_stub
    pressure_inputs = {
        "capacity_pressure": cap_p,
        "mutation_pressure": mut_p,
        "combat_exposure": comb_e,
        "repair_burden": rep_b
    }
    
    dest_floor = current_floor + 1 if traversal_type == "advance" else 0
    
    traversal_res = traversal_pressure_stub.make_traversal_event(
        player_id="console_player",
        source_floor_id=current_floor,
        destination_floor_id=dest_floor,
        traversal_type=traversal_type,
        pressure_inputs=pressure_inputs,
        route=selected_route,
        debug=debug
    )
    
    if not traversal_res["ok"]:
         return {"ok": False, "command": traversal_type, "message": traversal_res["message"], "payload": None, "error": "TraversalError"}

    traversal_event = traversal_res["traversal_event"]
    
    # 6. Route Result through Outcome Pipeline
    outcome = "VICTORY_ASCEND" if traversal_type == "advance" else "RETREAT_TO_HUB"
    pipeline_result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(tower_state, outcome, debug=debug)
    
    if not pipeline_result["ok"]:
        msg = pipeline_result.get("message")
        if not msg and "error" in pipeline_result:
            msg = pipeline_result["error"].get("message")
        return {"ok": False, "command": traversal_type, "message": f"Outcome resolution failed: {msg}", "payload": None, "error": pipeline_result.get("error_type")}
    
    # Update state
    session_state["runtime_context"]["tower_state"] = pipeline_result["tower_state"]
    
    msg = f"Traversal ({traversal_type}) successful. {traversal_res['summary']}"
    if traversal_type == "advance":
        msg += f" New floor: {pipeline_result['current_floor']}."
    else:
        msg += " Returned to Hub."

    payload = {
        "traversal_event": traversal_event,
        "traversal_summary": traversal_res["summary"],
        "traversal_pressure": traversal_event["traversal_pressure"].get("total_pressure", 0.0),
        "escape_risk": traversal_event["escape_risk"],
        "route_exposure": traversal_event["route_exposure"],
        "pipeline_result": pipeline_result,
        "room_graph": room_graph,
        "room_routes": room_routes,
        "selected_route": selected_route,
        "route_id": selected_route.get("route_id") if selected_route else None,
        "route_type": selected_route.get("route_type") if selected_route else None,
        "environmental_profile": selected_route.get("environmental_profile") if selected_route else None,
        "escape_modifier": selected_route.get("escape_modifier") if selected_route else None,
        "route_pressure_used": selected_route is not None
    }
    
    return {"ok": True, "command": traversal_type, "message": msg, "payload": payload, "error": None}


def _handle_help():
    commands = [
        "status   - Show current tower status.",
        "ascend   - Victory! Ascend to the next floor.",
        "advance  - Attempt spatial traversal to next floor.",
        "defeat   - Defeat! Drop back and trigger mutation/marks.",
        "retreat  - Retreat to the Hub.",
        "escape   - Attempt spatial escape back to Hub.",
        "diff     - Show changes from the latest defeat.",
        "marks    - List unclaimed survivor marks on current floor.",
        "claim ID - Claim a survivor mark by its ID.",
        "combat V - Resolve combat stub (safe|dangerous|exhausted).",
        "potion Q - Consume Q Ash Potions from inventory (default 1).",
        "repair Q - Deduct Q Repair Materials from inventory (default 1).",
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
