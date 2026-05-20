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

    # Escape resolution observation (TOWER-ENGINE-102)
    escape_resolutions_observed = 0
    escape_successes_observed = 0
    escape_partials_observed = 0
    escape_failures_observed = 0
    severe_escape_failures_observed = 0
    escape_residue_written_observed = False
    escape_mutation_pressure_observed = False
    total_escape_mutation_pressure_delta = 0.0
    escape_resource_losses_observed = []
    escape_pipeline_outcomes_observed = []
    escape_recoverability_preserved = True
    escape_floor_identity_preserved = True
    escape_resolution_summaries = []

    # Domain dashboard observation (TOWER-ENGINE-107)
    dashboard_snapshots_observed = 0
    dashboard_status_observed = False
    pressure_summaries_observed = []
    resource_summaries_observed = []
    equipment_summaries_observed = []
    route_summaries_observed = []
    residue_summaries_observed = []
    recoverability_statuses_observed = []
    dashboard_survival_summaries = []

    # Domain claim observation (TOWER-ENGINE-113)
    domain_claims_observed = 0
    domain_claim_types_observed = []
    highest_domain_maintenance_pressure_observed = 0.0
    highest_domain_visibility_pressure_observed = 0.0
    highest_domain_mutation_threat_observed = 0.0
    total_domain_recovery_value_observed = 0.0
    tower_hostility_preserved_observed = True
    domain_claim_summaries = []

    # Domain upkeep observation (TOWER-ENGINE-122)
    upkeep_events_observed = 0
    total_shards_consumed_observed = 0
    foothold_decay_events_observed = 0
    foothold_restoration_events_observed = 0
    upkeep_summaries = []

    # Tower reclamation observation (TOWER-ENGINE-122)
    reclamation_pressure_observed = False
    reclamation_pressure_values_observed = []
    highest_reclamation_pressure_observed = 0.0
    reclamation_bands_observed = []
    reclamation_summaries = []

    # Mutation scarring observation (TOWER-ENGINE-131)
    scarred_nodes_observed = 0
    highest_scar_intensity_observed = 0.0
    aggregate_hazard_bias_observed = 0.0
    scarring_summaries = []

    # Claim targeting observation (TOWER-ENGINE-131)
    highest_targeting_pressure_observed = 0.0
    foothold_destabilization_events_observed = 0
    targeting_summaries = []

    # Territorial instability & foothold collapse observation (Stage-018 / TOWER-ENGINE-149)
    territorial_instability_observed = False
    highest_territorial_instability_observed = 0.0
    unstable_footholds_observed = 0
    territorial_instability_summaries = []

    foothold_collapse_observed = False
    highest_foothold_collapse_level_observed = 0.0
    collapsed_footholds_observed = 0
    foothold_collapse_bands_observed = []
    foothold_collapse_summaries = []

    # Foothold recovery & scar mitigation observation (Stage-019 / TOWER-ENGINE-158)
    foothold_recovery_observed = False
    recovery_actions_observed = 0
    total_recovery_shards_spent_observed = 0.0
    recovery_restored_to_active_observed = 0
    recovery_restored_from_overrun_observed = 0
    recovery_summaries = []

    scar_mitigation_actions_observed = 0
    total_mitigation_shards_spent_observed = 0.0
    highest_scar_mitigation_credit_observed = 0.0
    scar_mitigation_summaries = []

    # Manual route selection observation (TOWER-ENGINE-140)
    route_selections_observed = 0
    strategic_biases_observed = []
    route_hazard_visibility_summaries = []
    
    # Hazard visibility observation (TOWER-ENGINE-140)
    average_information_accuracy_observed = 0.0
    highest_information_accuracy_observed = 0.0
    visibility_bands_observed = []

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

                    # Escape resolution specific (TOWER-ENGINE-102)
                    if res_cmd == "escape_attempt":
                        esc_res = payload.get("escape_resolution")
                        if esc_res:
                            escape_resolutions_observed += 1
                            outcome = esc_res.get("outcome")
                            if outcome == "ESCAPE_SUCCESS":
                                escape_successes_observed += 1
                            elif outcome == "ESCAPE_PARTIAL":
                                escape_partials_observed += 1
                            elif outcome.startswith("ESCAPE_FAILED"):
                                escape_failures_observed += 1
                                if outcome == "ESCAPE_FAILED_RETREAT_DROP":
                                    severe_escape_failures_observed += 1
                            
                            if esc_res.get("residue_written"):
                                escape_residue_written_observed = True
                            
                            delta = esc_res.get("mutation_pressure_delta", 0.0)
                            if delta > 0:
                                escape_mutation_pressure_observed = True
                                total_escape_mutation_pressure_delta += delta
                                
                            loss = esc_res.get("resource_loss")
                            if loss:
                                escape_resource_losses_observed.append(loss)
                            
                            pipe_outcome = esc_res.get("pipeline_outcome")
                            if pipe_outcome:
                                escape_pipeline_outcomes_observed.append(pipe_outcome)
                            
                            if not esc_res.get("recoverability_preserved"):
                                escape_recoverability_preserved = False
                            if not esc_res.get("floor_identity_preserved"):
                                escape_floor_identity_preserved = False
                                
                            escape_resolution_summaries.append(f"Escape resolved to {outcome}. Pipeline: {pipe_outcome}.")

                    # Domain dashboard specific (TOWER-ENGINE-107)
                    if res_cmd == "status" and result["ok"]:
                        snapshot = payload.get("dashboard_snapshot")
                        if snapshot:
                            dashboard_snapshots_observed += 1
                            dashboard_status_observed = True
                            
                            pressure_summaries_observed.append(snapshot.get("pressure_summary"))
                            resource_summaries_observed.append(snapshot.get("resource_summary"))
                            equipment_summaries_observed.append(snapshot.get("equipment_summary"))
                            route_summaries_observed.append(snapshot.get("route_summary"))
                            residue_summaries_observed.append(snapshot.get("residue_summary"))
                            recoverability_statuses_observed.append(snapshot.get("recoverability_status"))
                            
                            dashboard_survival_summaries.append(payload.get("dashboard_summary"))
                            
                            # Reclamation specific (TOWER-ENGINE-122)
                            reclamation = payload.get("reclamation_pressure")
                            if reclamation:
                                reclamation_pressure_observed = True
                                reclamation_pressure_values_observed.append(reclamation.get("total_reclamation_pressure", 0.0))
                                highest_reclamation_pressure_observed = max(highest_reclamation_pressure_observed, reclamation.get("total_reclamation_pressure", 0.0))
                                rb = reclamation.get("reclamation_band")
                                if rb and rb not in reclamation_bands_observed:
                                    reclamation_bands_observed.append(rb)
                                
                                rec_sum = f"Floor {reclamation.get('floor_id')} Reclamation: {rb} ({reclamation.get('total_reclamation_pressure'):.2f})"
                                reclamation_summaries.append(rec_sum)
                                
                            # Scarring specific (TOWER-ENGINE-131)
                            scarring = payload.get("mutation_scarring")
                            if scarring:
                                scarred_nodes_observed = max(scarred_nodes_observed, scarring.get("scarred_nodes_count", 0))
                                highest_scar_intensity_observed = max(highest_scar_intensity_observed, scarring.get("highest_scar_intensity", 0.0))
                                aggregate_hazard_bias_observed = max(aggregate_hazard_bias_observed, scarring.get("aggregate_hazard_bias", 0.0))
                                
                                scar_sum = f"Floor {snapshot.get('floor_id')} Scarring: {scarring.get('highest_scar_intensity'):.2f} ({scarring.get('scarred_nodes_count')} nodes)"
                                if scar_sum not in scarring_summaries:
                                    scarring_summaries.append(scar_sum)
                                    
                            # Route Visibility specific (TOWER-ENGINE-140)
                            vis_summary = payload.get("route_visibility")
                            if vis_summary:
                                average_information_accuracy_observed = max(average_information_accuracy_observed, vis_summary.get("average_information_accuracy", 0.0))
                                highest_information_accuracy_observed = max(highest_information_accuracy_observed, vis_summary.get("reconnaissance_level", 0.0))
                                band = vis_summary.get("best_visibility_band")
                                if band and band not in visibility_bands_observed:
                                    visibility_bands_observed.append(band)

                            # Territorial Instability (Stage-018)
                            inst = payload.get("territorial_instability")
                            if inst:
                                territorial_instability_observed = True
                                highest_territorial_instability_observed = max(highest_territorial_instability_observed, inst.get("highest_instability", 0.0))
                                unstable_footholds_observed = max(unstable_footholds_observed, inst.get("unstable_footholds", 0))
                                inst_sum = f"Floor {snapshot.get('floor_id')} Instability: {inst.get('highest_instability', 0.0):.2f} ({inst.get('unstable_footholds', 0)} unstable)"
                                if inst_sum not in territorial_instability_summaries:
                                    territorial_instability_summaries.append(inst_sum)

                            # Foothold Collapse (Stage-018)
                            collapse = payload.get("foothold_collapse")
                            if collapse:
                                foothold_collapse_observed = True
                                highest_foothold_collapse_level_observed = max(highest_foothold_collapse_level_observed, collapse.get("highest_collapse_level", 0.0))
                                collapsed_footholds_observed = max(collapsed_footholds_observed, collapse.get("collapsed_footholds", 0))
                                for b in collapse.get("collapse_bands_observed", []) or []:
                                    if b not in foothold_collapse_bands_observed:
                                        foothold_collapse_bands_observed.append(b)
                                col_sum = f"Floor {snapshot.get('floor_id')} Collapse: {collapse.get('highest_collapse_level', 0.0):.2f} ({collapse.get('collapsed_footholds', 0)} footholds)"
                                if col_sum not in foothold_collapse_summaries:
                                    foothold_collapse_summaries.append(col_sum)

                            # Foothold Recovery (Stage-019)
                            recov = snapshot.get("foothold_recovery_summary") if snapshot else None
                            if recov:
                                foothold_recovery_observed = True
                                recovery_actions_observed = max(recovery_actions_observed, recov.get("recovery_actions_taken", 0))
                                total_recovery_shards_spent_observed = max(total_recovery_shards_spent_observed, recov.get("total_shards_spent", 0.0))
                                recovery_restored_to_active_observed = max(recovery_restored_to_active_observed, recov.get("restored_to_active", 0))
                                recovery_restored_from_overrun_observed = max(recovery_restored_from_overrun_observed, recov.get("restored_from_overrun", 0))

            # Domain claim specific (TOWER-ENGINE-113)
            if res_cmd == "claim" and result["ok"]:
                claim = payload.get("domain_claim")
                if claim:
                    domain_claims_observed += 1
                    ct = claim.get("claim_type")
                    if ct and ct not in domain_claim_types_observed:
                        domain_claim_types_observed.append(ct)
                    
                    highest_domain_maintenance_pressure_observed = max(highest_domain_maintenance_pressure_observed, claim.get("maintenance_pressure", 0.0))
                    highest_domain_visibility_pressure_observed = max(highest_domain_visibility_pressure_observed, claim.get("visibility_pressure", 0.0))
                    highest_domain_mutation_threat_observed = max(highest_domain_mutation_threat_observed, claim.get("mutation_threat", 0.0))
                    total_domain_recovery_value_observed += claim.get("recovery_value", 0.0)
                    
                    if not claim.get("tower_hostility_preserved", True):
                        tower_hostility_preserved_observed = False
                    
                    claim_sum = payload.get("claim_summary")
                    if claim_sum:
                        domain_claim_summaries.append(claim_sum)
                        
                    # Targeting specific (TOWER-ENGINE-131)
                    tp = payload.get("targeting_pressure")
                    if tp is not None:
                        highest_targeting_pressure_observed = max(highest_targeting_pressure_observed, tp)
                        if payload.get("is_destabilized"):
                            foothold_destabilization_events_observed += 1
                        
                        target_sum = f"Claim {claim.get('claim_id')[:8]} Targeted: {tp:.2f}. Penalty: +{payload.get('maintenance_penalty')}."
                        targeting_summaries.append(target_sum)
                        
            # Manual Route Selection specific (TOWER-ENGINE-140)
            if res_cmd in ["advance", "escape_attempt"] and result["ok"]:
                selection = payload.get("route_selection")
                if selection:
                    route_selections_observed += 1
                    bias = selection.get("strategic_bias")
                    if bias and bias not in strategic_biases_observed:
                        strategic_biases_observed.append(bias)
                    
                    hp = selection.get("hazard_profile", {})
                    vis_sum = f"Chose {selection.get('selected_route_id')} ({bias}). Hazards: C:{hp.get('combat_hazard'):.2f}, M:{hp.get('mutation_hazard'):.2f}."
                    route_hazard_visibility_summaries.append(vis_sum)

            # Domain upkeep specific (TOWER-ENGINE-122)
            if res_cmd == "maintain" and result["ok"]:
                upkeep_events_observed += 1
                total_shards_consumed_observed += payload.get("shards_consumed", 0)
                
                upkeep_events = payload.get("upkeep_events", [])
                for ue in upkeep_events:
                    if ue.get("current_state") in ["DECAYING", "OVERRUN"] and ue.get("previous_state") == "ACTIVE":
                         foothold_decay_events_observed += 1
                    if ue.get("current_state") == "ACTIVE" and ue.get("previous_state") in ["DECAYING", "OVERRUN"]:
                         foothold_restoration_events_observed += 1
                         
                upkeep_summaries.append(result.get("message"))

            # Foothold recovery action specific (Stage-019)
            if res_cmd == "recover" and result["ok"]:
                foothold_recovery_observed = True
                recovery_actions_observed += 1
                rr = payload.get("recovery_record") if isinstance(payload, dict) else None
                if rr:
                    total_recovery_shards_spent_observed += float(rr.get("shards_spent", 0.0) or 0.0)
                    if rr.get("new_status") == "ACTIVE" and rr.get("previous_status") != "ACTIVE":
                        recovery_restored_to_active_observed += 1
                    if rr.get("previous_status") == "OVERRUN" and rr.get("new_status") != "OVERRUN":
                        recovery_restored_from_overrun_observed += 1
                rs = payload.get("recovery_summary") if isinstance(payload, dict) else None
                if rs:
                    recovery_summaries.append(rs)

            # Scar mitigation action specific (Stage-019)
            if res_cmd == "mitigate" and result["ok"]:
                scar_mitigation_actions_observed += 1
                ma = payload.get("mitigation_action") if isinstance(payload, dict) else None
                if ma:
                    total_mitigation_shards_spent_observed += float(ma.get("shards_spent", 0.0) or 0.0)
                credits = payload.get("scar_mitigation_credits") if isinstance(payload, dict) else None
                if isinstance(credits, dict) and len(credits) > 0:
                    highest_scar_mitigation_credit_observed = max(highest_scar_mitigation_credit_observed, max(float(v or 0.0) for v in credits.values()))
                scar_mitigation_summaries.append(result.get("message"))

            inv_summary = payload.get("inventory_state_summary")
            if inv_summary and inv_summary not in inventory_summaries:
                inventory_summaries.append(inv_summary)

    # 3. Final State Capture
    transcript = {
        "transcript_id": transcript_id,
        "patch_id": "TOWER-ENGINE-140",
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
        "escape_resolutions_observed": escape_resolutions_observed,
        "escape_successes_observed": escape_successes_observed,
        "escape_partials_observed": escape_partials_observed,
        "escape_failures_observed": escape_failures_observed,
        "severe_escape_failures_observed": severe_escape_failures_observed,
        "escape_residue_written_observed": escape_residue_written_observed,
        "escape_mutation_pressure_observed": escape_mutation_pressure_observed,
        "total_escape_mutation_pressure_delta": total_escape_mutation_pressure_delta,
        "escape_resource_losses_observed": escape_resource_losses_observed,
        "escape_pipeline_outcomes_observed": escape_pipeline_outcomes_observed,
        "escape_recoverability_preserved": escape_recoverability_preserved,
        "escape_floor_identity_preserved": escape_floor_identity_preserved,
        "escape_resolution_summaries": escape_resolution_summaries,
        "dashboard_snapshots_observed": dashboard_snapshots_observed,
        "dashboard_status_observed": dashboard_status_observed,
        "pressure_summaries_observed": pressure_summaries_observed,
        "resource_summaries_observed": resource_summaries_observed,
        "equipment_summaries_observed": equipment_summaries_observed,
        "route_summaries_observed": route_summaries_observed,
        "residue_summaries_observed": residue_summaries_observed,
        "recoverability_statuses_observed": recoverability_statuses_observed,
        "dashboard_survival_summaries": dashboard_survival_summaries,
        "domain_claims_observed": domain_claims_observed,
        "domain_claim_types_observed": domain_claim_types_observed,
        "highest_domain_maintenance_pressure_observed": highest_domain_maintenance_pressure_observed,
        "highest_domain_visibility_pressure_observed": highest_domain_visibility_pressure_observed,
        "highest_domain_mutation_threat_observed": highest_domain_mutation_threat_observed,
        "total_domain_recovery_value_observed": total_domain_recovery_value_observed,
        "tower_hostility_preserved_observed": tower_hostility_preserved_observed,
        "domain_claim_summaries": domain_claim_summaries,
        "upkeep_events_observed": upkeep_events_observed,
        "total_shards_consumed_observed": total_shards_consumed_observed,
        "foothold_decay_events_observed": foothold_decay_events_observed,
        "foothold_restoration_events_observed": foothold_restoration_events_observed,
        "upkeep_summaries": upkeep_summaries,
        "reclamation_pressure_observed": reclamation_pressure_observed,
        "reclamation_pressure_values_observed": reclamation_pressure_values_observed,
        "highest_reclamation_pressure_observed": highest_reclamation_pressure_observed,
        "reclamation_bands_observed": reclamation_bands_observed,
        "reclamation_summaries": reclamation_summaries,
        "scarred_nodes_observed": scarred_nodes_observed,
        "highest_scar_intensity_observed": highest_scar_intensity_observed,
        "aggregate_hazard_bias_observed": aggregate_hazard_bias_observed,
        "scarring_summaries": scarring_summaries,
        "highest_targeting_pressure_observed": highest_targeting_pressure_observed,
        "foothold_destabilization_events_observed": foothold_destabilization_events_observed,
        "targeting_summaries": targeting_summaries,
        "territorial_instability_observed": territorial_instability_observed,
        "highest_territorial_instability_observed": highest_territorial_instability_observed,
        "unstable_footholds_observed": unstable_footholds_observed,
        "territorial_instability_summaries": territorial_instability_summaries,
        "foothold_collapse_observed": foothold_collapse_observed,
        "highest_foothold_collapse_level_observed": highest_foothold_collapse_level_observed,
        "collapsed_footholds_observed": collapsed_footholds_observed,
        "foothold_collapse_bands_observed": foothold_collapse_bands_observed,
        "foothold_collapse_summaries": foothold_collapse_summaries,
        "foothold_recovery_observed": foothold_recovery_observed,
        "recovery_actions_observed": recovery_actions_observed,
        "total_recovery_shards_spent_observed": float(round(total_recovery_shards_spent_observed, 4)),
        "recovery_restored_to_active_observed": recovery_restored_to_active_observed,
        "recovery_restored_from_overrun_observed": recovery_restored_from_overrun_observed,
        "recovery_summaries": recovery_summaries,
        "scar_mitigation_actions_observed": scar_mitigation_actions_observed,
        "total_mitigation_shards_spent_observed": float(round(total_mitigation_shards_spent_observed, 4)),
        "highest_scar_mitigation_credit_observed": float(round(highest_scar_mitigation_credit_observed, 4)),
        "scar_mitigation_summaries": scar_mitigation_summaries,
        "route_selections_observed": route_selections_observed,
        "strategic_biases_observed": strategic_biases_observed,
        "route_hazard_visibility_summaries": route_hazard_visibility_summaries,
        "average_information_accuracy_observed": average_information_accuracy_observed,
        "highest_information_accuracy_observed": highest_information_accuracy_observed,
        "visibility_bands_observed": visibility_bands_observed,
        "route_selections_observed": route_selections_observed,
        "strategic_biases_observed": strategic_biases_observed,
        "route_hazard_visibility_summaries": route_hazard_visibility_summaries,
        "average_information_accuracy_observed": average_information_accuracy_observed,
        "highest_information_accuracy_observed": highest_information_accuracy_observed,
        "visibility_bands_observed": visibility_bands_observed,
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
    # Specific ID for TOWER-ENGINE-140 validation artifact
    if transcript_id == "route_visibility_validation":
        filename = "tower_engine_140_route_visibility_console_transcript.json"
    elif transcript_id == "scarring_targeting_validation":
        filename = "tower_engine_131_scarring_targeting_console_transcript.json"
    elif transcript_id == "upkeep_reclamation_validation":
        filename = "tower_engine_122_upkeep_reclamation_console_transcript.json"
    elif transcript_id == "domain_claim_validation":
        filename = "tower_engine_113_domain_claim_console_transcript.json"
    elif transcript_id == "dashboard_snapshot_validation":
        filename = "tower_engine_107_dashboard_snapshot_console_transcript.json"
    elif transcript_id == "escape_resolution_validation":
        filename = "tower_engine_102_escape_resolution_console_transcript.json"
    elif transcript_id == "room_route_validation":
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
        filename = f"tower_engine_140_console_transcript_{transcript_id[:8]}.json"

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
        "patch_id": "TOWER-ENGINE-140",
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
        "escape_resolutions_observed": 0,
        "escape_successes_observed": 0,
        "escape_partials_observed": 0,
        "escape_failures_observed": 0,
        "severe_escape_failures_observed": 0,
        "escape_residue_written_observed": False,
        "escape_mutation_pressure_observed": False,
        "total_escape_mutation_pressure_delta": 0.0,
        "escape_resource_losses_observed": [],
        "escape_pipeline_outcomes_observed": [],
        "escape_recoverability_preserved": True,
        "escape_floor_identity_preserved": True,
        "escape_resolution_summaries": [],
        "dashboard_snapshots_observed": 0,
        "dashboard_status_observed": False,
        "pressure_summaries_observed": [],
        "resource_summaries_observed": [],
        "equipment_summaries_observed": [],
        "route_summaries_observed": [],
        "residue_summaries_observed": [],
        "recoverability_statuses_observed": [],
        "dashboard_survival_summaries": [],
        "domain_claims_observed": 0,
        "domain_claim_types_observed": [],
        "highest_domain_maintenance_pressure_observed": 0.0,
        "highest_domain_visibility_pressure_observed": 0.0,
        "highest_domain_mutation_threat_observed": 0.0,
        "total_domain_recovery_value_observed": 0.0,
        "tower_hostility_preserved_observed": True,
        "domain_claim_summaries": [],
        "upkeep_events_observed": 0,
        "total_shards_consumed_observed": 0,
        "foothold_decay_events_observed": 0,
        "foothold_restoration_events_observed": 0,
        "upkeep_summaries": [],
        "reclamation_pressure_observed": False,
        "reclamation_pressure_values_observed": [],
        "highest_reclamation_pressure_observed": 0.0,
        "reclamation_bands_observed": [],
        "reclamation_summaries": [],
        "scarred_nodes_observed": 0,
        "highest_scar_intensity_observed": 0.0,
        "aggregate_hazard_bias_observed": 0.0,
        "scarring_summaries": [],
        "highest_targeting_pressure_observed": 0.0,
        "foothold_destabilization_events_observed": 0,
        "targeting_summaries": [],
        "territorial_instability_observed": False,
        "highest_territorial_instability_observed": 0.0,
        "unstable_footholds_observed": 0,
        "territorial_instability_summaries": [],
        "foothold_collapse_observed": False,
        "highest_foothold_collapse_level_observed": 0.0,
        "collapsed_footholds_observed": 0,
        "foothold_collapse_bands_observed": [],
        "foothold_collapse_summaries": [],
        "foothold_recovery_observed": False,
        "recovery_actions_observed": 0,
        "total_recovery_shards_spent_observed": 0.0,
        "recovery_restored_to_active_observed": 0,
        "recovery_restored_from_overrun_observed": 0,
        "recovery_summaries": [],
        "scar_mitigation_actions_observed": 0,
        "total_mitigation_shards_spent_observed": 0.0,
        "highest_scar_mitigation_credit_observed": 0.0,
        "scar_mitigation_summaries": [],
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
