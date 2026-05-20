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
    attrition_pressure_observed = True if False else False # Placeholder to avoid unused warnings if needed
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
    
    # Inventory observation
    inventory_transactions_observed = 0
    inventory_applications_observed = 0
    inventory_failures_observed = 0
    total_gold_added_to_inventory = 0
    items_added_to_inventory = []
    items_deducted_from_inventory = []
    capacity_pressure_observed = False
    capacity_pressure_values_observed = []
    capacity_bands_observed = []
    highest_capacity_pressure_observed = 0.0
    over_capacity_failures_observed = 0
    inventory_summaries = []
    material_burden_summaries = []
    
    # Consumable drain observation (TOWER-ENGINE-067)
    consumable_uses_observed = 0
    consumables_deducted_observed = 0
    failed_consumable_attempts_observed = 0
    potion_drain_observed = False
    total_potions_consumed = 0
    consumable_drain_summaries = []

    # Repair material observation (TOWER-ENGINE-069)
    repair_material_uses_observed = 0
    repair_materials_deducted_observed = 0
    failed_repair_attempts_observed = 0
    repair_material_drain_observed = False
    durability_restoration_observed = False
    repair_drain_summaries = []

    # Repair runtime observation (TOWER-ENGINE-083)
    repair_events_observed = 0
    repair_applications_observed = 0
    repair_failures_observed = 0
    total_durability_restored_observed = 0.0
    repair_materials_consumed_observed = 0
    equipment_items_repaired_observed = []
    bounded_repair_clean = True
    repair_runtime_summaries = []

    # Traversal observation (TOWER-ENGINE-089)
    traversal_events_observed = 0
    advance_attempts_observed = 0
    escape_attempts_observed = 0
    traversal_pressure_observed = False
    traversal_pressure_values_observed = []
    highest_traversal_pressure_observed = 0.0
    escape_risk_observed = False
    escape_risk_values_observed = []
    highest_escape_risk_observed = 0.0
    route_exposure_values_observed = []
    traversal_summaries = []

    # Room route observation (TOWER-ENGINE-096)
    room_route_evidence_observed = False
    room_routes_observed = 0
    selected_routes_observed = []
    route_types_observed = []
    environmental_profiles_observed = []
    highest_route_exposure_observed = 0.0
    escape_modifiers_observed = []
    route_pressure_used_observed = False
    room_route_summaries = []

    # Durability decay observation (TOWER-ENGINE-079)
    durability_decay_observed = False
    durability_events_observed = 0
    total_durability_loss_observed = 0.0
    equipment_items_worn_observed = []
    zero_durability_items_observed = []
    durability_pressure_observed = False
    durability_decay_summaries = []
    
    # Room graph evidence observation
    room_graph_evidence_observed = False
    room_graph_changes_observed = 0
    survivor_mark_rooms_observed = 0
    graph_diff_summaries = []
    
    # Pre-capture context for loop use
    tower_state = session_state["runtime_context"]["tower_state"]
    player_prog = session_state["runtime_context"]["player_progression"]

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
                        survivor_mark_rooms_added = payload.get("survivor_mark_room_added", False)
                        if survivor_mark_rooms_added:
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

            # Extract durability decay evidence (TOWER-ENGINE-079)
            if payload.get("durability_decay_applied"):
                durability_decay_observed = True
                if payload.get("durability_pressure_observed"):
                    durability_pressure_observed = True
                
                events = payload.get("durability_events", [])
                for event in events:
                    durability_events_observed += 1
                    total_durability_loss_observed += event.get("durability_loss", 0)
                    
                    item_id = event.get("equipment_item_id")
                    if item_id:
                        if item_id not in equipment_items_worn_observed:
                            equipment_items_worn_observed.append(item_id)
                        if event.get("durability_after") == 0:
                            if item_id not in zero_durability_items_observed:
                                zero_durability_items_observed.append(item_id)
                    
                    # Basic summary from event
                    summary = f"Item {item_id} lost {event.get('durability_loss')} durability. Remaining: {event.get('durability_after')}/{event.get('maximum_durability')}"
                    if summary not in durability_decay_summaries:
                        durability_decay_summaries.append(summary)

        # Extract inventory and consumable evidence (TOWER-ENGINE-065/067/069/073/083)
        if isinstance(payload, dict):
            inv_tx = payload.get("inventory_transaction")
            if inv_tx:
                inventory_transactions_observed += 1
                applied = inv_tx.get("transaction_applied", False)
                if applied:
                    inventory_applications_observed += 1
                    
                    # Accumulate gold
                    delta = inv_tx.get("currency_delta", {})
                    total_gold_added_to_inventory += delta.get("gold", 0)
                    
                    # Capture items
                    items_added_to_inventory.extend(inv_tx.get("items_added", []))
                    items_deducted_from_inventory.extend(inv_tx.get("items_deducted", []))
                else:
                    inventory_failures_observed += 1
                
                # Check capacity pressure (TOWER-ENGINE-073)
                cap_after = inv_tx.get("capacity_after", 0)
                if cap_after > 0:
                    capacity_pressure_observed = True
                
                # Consumable specific (TOWER-ENGINE-067)
                if res_cmd == "potion":
                    if applied:
                        consumable_uses_observed += 1
                        potion_drain_observed = True
                        qty = payload.get("quantity_requested", 0)
                        total_potions_consumed += qty
                        consumables_deducted_observed += qty
                        consumable_drain_summaries.append(f"Successfully consumed {qty} potions.")
                    else:
                        failed_consumable_attempts_observed += 1
                        consumable_drain_summaries.append(f"Failed potion attempt: {result.get('message')}")

                # Repair material specific (TOWER-ENGINE-069/083)
                if res_cmd == "repair":
                    repair_events_observed += 1
                    if applied:
                        repair_material_uses_observed += 1
                        repair_material_drain_observed = True
                        qty = payload.get("quantity_requested", 0)
                        repair_materials_deducted_observed += qty
                        repair_drain_summaries.append(f"Successfully deducted {qty} repair materials.")
                        
                        # Repair runtime specific (TOWER-ENGINE-083)
                        repair_applications_observed += 1
                        repair_materials_consumed_observed += qty
                        
                        repair_event = payload.get("repair_event")
                        if repair_event:
                            total_durability_restored_observed += repair_event.get("durability_restored", 0.0)
                            item_id = repair_event.get("equipment_item_id")
                            if item_id and item_id not in equipment_items_repaired_observed:
                                equipment_items_repaired_observed.append(item_id)
                            
                            # Verify boundedness
                            if repair_event.get("durability_after", 0) > repair_event.get("maximum_durability", 1):
                                bounded_repair_clean = False
                            if not repair_event.get("bounded_flags_clean"):
                                bounded_repair_clean = False
                                
                            repair_runtime_summaries.append(f"Item {item_id} restored {repair_event.get('durability_restored')} durability.")
                    else:
                        failed_repair_attempts_observed += 1
                        repair_failures_observed += 1
                        repair_drain_summaries.append(f"Failed repair attempt: {result.get('message')}")
                        repair_runtime_summaries.append(f"Repair attempt failed: {result.get('message')}")
            
            # Extract capacity pressure summary (TOWER-ENGINE-073)
            cap_summary = payload.get("capacity_pressure_summary")
            if cap_summary:
                capacity_pressure_observed = True
                pressure_val = cap_summary.get("capacity_pressure", 0.0)
                capacity_pressure_values_observed.append(pressure_val)
                highest_capacity_pressure_observed = max(highest_capacity_pressure_observed, pressure_val)
                
                band = cap_summary.get("capacity_band")
                if band and band not in capacity_bands_observed:
                    capacity_bands_observed.append(band)
                
                if cap_summary.get("over_capacity"):
                    over_capacity_failures_observed += 1
                
                # Add to material burden summaries
                burden_sum = f"Floor {tower_state.get('current_floor')} Burden: {cap_summary.get('used_capacity')}/{cap_summary.get('inventory_capacity')} ({band})"
                if burden_sum not in material_burden_summaries:
                    material_burden_summaries.append(burden_sum)
            
            # Traversal observation (TOWER-ENGINE-089/096)
            if res_cmd in ["advance", "escape_attempt", "status"]:
                if result["ok"]:
                    if res_cmd == "advance":
                        traversal_events_observed += 1
                        advance_attempts_observed += 1
                    elif res_cmd == "escape_attempt":
                        traversal_events_observed += 1
                        escape_attempts_observed += 1
                    
                    if payload.get("traversal_summary"):
                        traversal_summaries.append(payload.get("traversal_summary"))
                    elif payload.get("traversal_pressure_summary"):
                        traversal_summaries.append(f"Status check: {payload.get('traversal_pressure_summary')}")
                    
                    tp = payload.get("traversal_pressure")
                    if tp is not None:
                        traversal_pressure_observed = True
                        traversal_pressure_values_observed.append(tp)
                        highest_traversal_pressure_observed = max(highest_traversal_pressure_observed, tp)
                    
                    risk = payload.get("escape_risk")
                    if risk is not None:
                        escape_risk_observed = True
                        escape_risk_values_observed.append(risk)
                        highest_escape_risk_observed = max(highest_escape_risk_observed, risk)
                    
                    re = payload.get("route_exposure")
                    if re is not None:
                        route_exposure_values_observed.append(re)
                        highest_route_exposure_observed = max(highest_route_exposure_observed, re)

                    # Room route specific (TOWER-ENGINE-096)
                    if payload.get("room_graph"):
                        room_graph_evidence_observed = True
                    
                    if payload.get("room_routes"):
                        room_route_evidence_observed = True
                        room_routes_observed += len(payload.get("room_routes", []))
                    
                    selected_route = payload.get("selected_route")
                    if selected_route:
                        selected_routes_observed.append(selected_route.get("route_id"))
                        route_type = selected_route.get("route_type")
                        if route_type:
                            route_types_observed.append(route_type)
                        
                        env_profile = selected_route.get("environmental_profile")
                        if env_profile:
                            environmental_profiles_observed.append(env_profile)
                        
                        esc_mod = selected_route.get("escape_modifier")
                        if esc_mod is not None:
                            escape_modifiers_observed.append(esc_mod)
                        
                        if payload.get("route_pressure_used"):
                            route_pressure_used_observed = True
                            
                        room_route_summaries.append(f"Chose {route_type} route {selected_route.get('route_id')} (Exposure: {selected_route.get('route_exposure')})")

            inv_summary = payload.get("inventory_state_summary")
            if inv_summary and inv_summary not in inventory_summaries:
                inventory_summaries.append(inv_summary)

    # 3. Final State Capture
    transcript = {
        "transcript_id": transcript_id,
        "patch_id": "TOWER-ENGINE-096",
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
        "inventory_transactions_observed": inventory_transactions_observed,
        "inventory_applications_observed": inventory_applications_observed,
        "inventory_failures_observed": inventory_failures_observed,
        "total_gold_added_to_inventory": total_gold_added_to_inventory,
        "items_added_to_inventory": items_added_to_inventory,
        "items_deducted_from_inventory": items_deducted_from_inventory,
        "capacity_pressure_observed": capacity_pressure_observed,
        "capacity_pressure_values_observed": capacity_pressure_values_observed,
        "capacity_bands_observed": capacity_bands_observed,
        "highest_capacity_pressure_observed": highest_capacity_pressure_observed,
        "over_capacity_failures_observed": over_capacity_failures_observed,
        "material_burden_summaries": material_burden_summaries,
        "inventory_summaries": inventory_summaries,
        "consumable_uses_observed": consumable_uses_observed,
        "consumables_deducted_observed": consumables_deducted_observed,
        "failed_consumable_attempts_observed": failed_consumable_attempts_observed,
        "potion_drain_observed": potion_drain_observed,
        "total_potions_consumed": total_potions_consumed,
        "consumable_drain_summaries": consumable_drain_summaries,
        "repair_material_uses_observed": repair_material_uses_observed,
        "repair_materials_deducted_observed": repair_materials_deducted_observed,
        "failed_repair_attempts_observed": failed_repair_attempts_observed,
        "repair_material_drain_observed": repair_material_drain_observed,
        "durability_restoration_observed": durability_restoration_observed,
        "repair_drain_summaries": repair_drain_summaries,
        "repair_events_observed": repair_events_observed,
        "repair_applications_observed": repair_applications_observed,
        "repair_failures_observed": repair_failures_observed,
        "total_durability_restored_observed": total_durability_restored_observed,
        "repair_materials_consumed_observed": repair_materials_consumed_observed,
        "equipment_items_repaired_observed": equipment_items_repaired_observed,
        "bounded_repair_clean": bounded_repair_clean,
        "repair_runtime_summaries": repair_runtime_summaries,
        "traversal_events_observed": traversal_events_observed,
        "advance_attempts_observed": advance_attempts_observed,
        "escape_attempts_observed": escape_attempts_observed,
        "traversal_pressure_observed": traversal_pressure_observed,
        "traversal_pressure_values_observed": traversal_pressure_values_observed,
        "highest_traversal_pressure_observed": highest_traversal_pressure_observed,
        "escape_risk_observed": escape_risk_observed,
        "escape_risk_values_observed": escape_risk_values_observed,
        "highest_escape_risk_observed": highest_escape_risk_observed,
        "route_exposure_values_observed": route_exposure_values_observed,
        "traversal_summaries": traversal_summaries,
        "room_graph_evidence_observed": room_graph_evidence_observed,
        "room_route_evidence_observed": room_route_evidence_observed,
        "room_routes_observed": room_routes_observed,
        "selected_routes_observed": selected_routes_observed,
        "route_types_observed": route_types_observed,
        "environmental_profiles_observed": environmental_profiles_observed,
        "highest_route_exposure_observed": highest_route_exposure_observed,
        "escape_modifiers_observed": escape_modifiers_observed,
        "route_pressure_used_observed": route_pressure_used_observed,
        "room_route_summaries": room_route_summaries,
        "durability_decay_observed": durability_decay_observed,
        "durability_events_observed": durability_events_observed,
        "total_durability_loss_observed": total_durability_loss_observed,
        "equipment_items_worn_observed": equipment_items_worn_observed,
        "zero_durability_items_observed": zero_durability_items_observed,
        "durability_pressure_observed": durability_pressure_observed,
        "durability_decay_summaries": durability_decay_summaries,
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
    # Specific ID for TOWER-ENGINE-096 validation artifact
    if transcript_id == "room_route_validation":
        filename = "tower_engine_096_room_route_evidence_console_transcript.json"
    elif transcript_id == "traversal_evidence_validation":
        filename = "tower_engine_089_traversal_evidence_console_transcript.json"
    elif transcript_id == "repair_runtime_validation":
        filename = "tower_engine_083_repair_runtime_console_transcript.json"
    elif transcript_id == "durability_decay_validation":
        filename = "tower_engine_079_durability_decay_console_transcript.json"
    elif transcript_id == "capacity_pressure_validation":
        filename = "tower_engine_073_capacity_pressure_console_transcript.json"
    elif transcript_id == "repair_material_drain_validation":
        filename = "tower_engine_069_repair_material_drain_console_transcript.json"
    elif transcript_id == "consumable_drain_validation":
        filename = "tower_engine_067_consumable_drain_console_transcript.json"
    elif transcript_id == "inventory_evidence_validation":
        filename = "tower_engine_065_inventory_evidence_console_transcript.json"
    elif transcript_id == "loot_evidence_validation":
        filename = "tower_engine_054_loot_evidence_console_transcript.json"
    elif transcript_id == "enemy_pressure_validation":
        filename = "tower_engine_050_enemy_pressure_console_transcript.json"
    elif transcript_id == "graph_combat_validation":
        filename = "tower_engine_045_graph_combat_console_transcript.json"
    else:
        filename = f"tower_engine_096_console_transcript_{transcript_id[:8]}.json"

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
        "patch_id": "TOWER-ENGINE-096",
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
        "inventory_transactions_observed": 0,
        "inventory_applications_observed": 0,
        "inventory_failures_observed": 0,
        "total_gold_added_to_inventory": 0,
        "items_added_to_inventory": [],
        "items_deducted_from_inventory": [],
        "capacity_pressure_observed": False,
        "capacity_pressure_values_observed": [],
        "capacity_bands_observed": [],
        "highest_capacity_pressure_observed": 0.0,
        "over_capacity_failures_observed": 0,
        "material_burden_summaries": [],
        "inventory_summaries": [],
        "consumable_uses_observed": 0,
        "consumables_deducted_observed": 0,
        "failed_consumable_attempts_observed": 0,
        "potion_drain_observed": False,
        "total_potions_consumed": 0,
        "consumable_drain_summaries": [],
        "repair_material_uses_observed": 0,
        "repair_materials_deducted_observed": 0,
        "failed_repair_attempts_observed": 0,
        "repair_material_drain_observed": False,
        "durability_restoration_observed": False,
        "repair_drain_summaries": [],
        "repair_events_observed": 0,
        "repair_applications_observed": 0,
        "repair_failures_observed": 0,
        "total_durability_restored_observed": 0.0,
        "repair_materials_consumed_observed": 0,
        "equipment_items_repaired_observed": [],
        "bounded_repair_clean": True,
        "repair_runtime_summaries": [],
        "traversal_events_observed": 0,
        "advance_attempts_observed": 0,
        "escape_attempts_observed": 0,
        "traversal_pressure_observed": False,
        "traversal_pressure_values_observed": [],
        "highest_traversal_pressure_observed": 0.0,
        "escape_risk_observed": False,
        "escape_risk_values_observed": [],
        "highest_escape_risk_observed": 0.0,
        "route_exposure_values_observed": [],
        "traversal_summaries": [],
        "room_graph_evidence_observed": False,
        "room_route_evidence_observed": False,
        "room_routes_observed": 0,
        "selected_routes_observed": [],
        "route_types_observed": [],
        "environmental_profiles_observed": [],
        "highest_route_exposure_observed": 0.0,
        "escape_modifiers_observed": [],
        "route_pressure_used_observed": False,
        "room_route_summaries": [],
        "durability_decay_observed": False,
        "durability_events_observed": 0,
        "total_durability_loss_observed": 0.0,
        "equipment_items_worn_observed": [],
        "zero_durability_items_observed": [],
        "durability_pressure_observed": False,
        "durability_decay_summaries": [],
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
