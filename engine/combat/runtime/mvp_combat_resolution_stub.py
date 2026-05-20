import os
import json
import uuid
import datetime

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import MVP systems
try:
    from engine.prototype.runtime import mvp_outcome_pipeline
    from engine.save.runtime import json_save_manager
    from engine.equipment.runtime import equipment_pressure_stub
    from engine.equipment.durability import durability_decay_stub
    _dependencies_available = True
except ImportError:
    _dependencies_available = False

# Path to combat session schema
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_COMBAT_SESSION_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/combat/contracts/combat_session.schema.json")


def _log_debug_event(patch_id, system, severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        event = debug_logger.make_debug_event(patch_id, system, severity, event_type, message, context)
        debug_logger.write_debug_event(event)
    elif not _debug_logger_available and debug_enabled:
        print(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: {message}")


def make_combat_session(floor_id, player_state, enemy_pressure_rating=0.25, resource_usage=None, enemy_pressure_profile=None, equipment_loadout=None, traversal_pressure_summary=None, selected_route=None, debug=False):
    """
    Creates a combat session object compatible with the project schema.
    """
    if resource_usage is None:
        resource_usage = {
            "potions_used": 0,
            "repair_items_used": 0,
            "recovery_events": 0
        }

    # Default player stats if not fully provided
    p_stats = {
        "health": player_state.get("health", 100.0),
        "damage": player_state.get("damage", 10.0),
        "defense": player_state.get("defense", 5.0),
        "speed": player_state.get("speed", 1.0),
        "recovery": player_state.get("recovery", 0.5)
    }

    # If profile is provided, it may set or bias the pressure rating
    final_pressure_rating = enemy_pressure_rating
    if enemy_pressure_profile:
        # Use profile rating if it's higher than the provided baseline
        final_pressure_rating = max(final_pressure_rating, enemy_pressure_profile.get("base_pressure_rating", 0.0))

    # Handle equipment pressure (TOWER-ENGINE-059/077)
    equipment_pressure = None
    capacity_pressure = 0.0
    if equipment_loadout:
        # Loadout object from Stage 007/008 has aggregate_pressure
        # But we still use equipment_pressure_stub to be sure or to handle raw item lists
        equipment_pressure = equipment_pressure_stub.calculate_aggregate_equipment_pressure(
            equipment_loadout.get("equipped_items", []), debug=debug
        )
        # Capacity pressure is explicitly required in session (TOWER-ENGINE-077)
        if "aggregate_pressure" in equipment_loadout:
            capacity_pressure = equipment_loadout["aggregate_pressure"].get("capacity_pressure", 0.0)
        elif equipment_pressure:
            capacity_pressure = equipment_pressure.get("capacity_pressure", 0.0)

    combat_session = {
        "combat_session_id": f"combat_{uuid.uuid4()}",
        "floor_id": floor_id,
        "player_id": player_state.get("player_id", "player_default"),
        "enemy_group_id": f"enemy_group_{floor_id}",
        "combat_tick": 0,
        "player_stats": p_stats,
        "enemy_pressure_rating": final_pressure_rating,
        "resource_usage": resource_usage,
        "residue_pressure": {
            "dominant_build_visibility": 0.0,
            "strategy_repetition_pressure": 0.0,
            "counter_pressure": 0.0
        },
        "predicted_outcome": "VICTORY_ASCEND", # Initial guess
        "forbidden_flags": {
            "permanent_invulnerability": False,
            "infinite_damage_scaling": False,
            "resource_bypass": False,
            "pipeline_bypass": False
        },
        "enemy_pressure_profile": enemy_pressure_profile,
        "enemy_archetype_id": enemy_pressure_profile.get("enemy_archetype_id") if enemy_pressure_profile else None,
        "enemy_adaptation_reasoning": enemy_pressure_profile.get("adaptation_reasoning", []) if enemy_pressure_profile else [],
        "equipment_loadout": equipment_loadout,
        "equipment_pressure": equipment_pressure,
        "equipment_pressure_used": equipment_pressure is not None,
        "capacity_pressure": capacity_pressure,
        "traversal_pressure_summary": traversal_pressure_summary,
        "traversal_pressure_used": traversal_pressure_summary is not None,
        "selected_route": selected_route,
        "room_route_bias_used": selected_route is not None
    }

    _log_debug_event("TOWER-ENGINE-077", "combat_resolution_stub", "INFO", "SessionCreated", f"Combat session created for floor {floor_id}.", {"session_id": combat_session["combat_session_id"]}, debug)
    return combat_session


def validate_combat_session(combat_session, schema_path=None, debug=False):
    """
    Validates a combat session against its schema.
    """
    if not _dependencies_available:
        return {"ok": False, "message": "json_save_manager not available."}

    if schema_path is None:
        schema_path = _COMBAT_SESSION_SCHEMA_PATH

    return json_save_manager.validate_json(combat_session, schema_path, debug=debug)


def resolve_combat_session(combat_session, debug=False):
    """
    Deterministic resolution of combat based on session inputs.
    """
    _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "INFO", "ResolutionStart", "Resolving combat session.", {"session_id": combat_session["combat_session_id"]}, debug)

    player_health = combat_session["player_stats"].get("health", 0)
    enemy_pressure = combat_session["enemy_pressure_rating"]
    potions_used = combat_session["resource_usage"].get("potions_used", 0)
    profile = combat_session.get("enemy_pressure_profile")
    archetype_id = profile.get("enemy_archetype_id") if profile else None
    
    # Equipment Pressure (TOWER-ENGINE-059/077)
    eq_loadout = combat_session.get("equipment_loadout")
    eq_pressure = combat_session.get("equipment_pressure")
    eq_used = combat_session.get("equipment_pressure_used", False)
    capacity_p = combat_session.get("capacity_pressure", 0.0)

    # Traversal Pressure (TOWER-ENGINE-090)
    trav_summary = combat_session.get("traversal_pressure_summary")
    trav_used = combat_session.get("traversal_pressure_used", False)
    traversal_bias_reasoning = []
    
    trav_p = 0.0
    esc_r = 0.0
    rou_e = 0.0
    if trav_used and trav_summary:
        # If it's a full event
        if "traversal_event" in trav_summary:
            event = trav_summary["traversal_event"]
            trav_p = event.get("traversal_pressure", {}).get("total_pressure", 0.0)
            esc_r = event.get("escape_risk", 0.0)
            rou_e = event.get("route_exposure", 0.0)
        else:
            # If it's a flat summary object
            trav_p = trav_summary.get("traversal_pressure", 0.0)
            esc_r = trav_summary.get("escape_risk", 0.0)
            rou_e = trav_summary.get("route_exposure", 0.0)

    # Room Route Bias (TOWER-ENGINE-097)
    selected_route = combat_session.get("selected_route")
    route_used = combat_session.get("room_route_bias_used", False)
    room_route_bias_reasoning = []
    
    route_exp = 0.0
    env_profile = None
    esc_mod = 0.0
    
    if route_used and selected_route:
        route_exp = selected_route.get("route_exposure", 0.0)
        env_profile = selected_route.get("environmental_profile", {})
        esc_mod = selected_route.get("escape_modifier", 0.0)

    outcome = "VICTORY_ASCEND" # Default

    # Apply biases to outcome
    effective_pressure = enemy_pressure
    
    # Archetype biases
    if archetype_id == "ambush_unit" and player_health < 40:
        effective_pressure += 0.2
        _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "DEBUG", "AmbushBias", "Increasing defeat risk due to ambush unit at low health.", debug_enabled=debug)

    # Equipment risk bias
    if eq_used and eq_pressure.get("risk_profile", 0.0) > 0.7 and enemy_pressure > 0.6:
        effective_pressure += 0.15
        _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "DEBUG", "EquipmentRiskBias", "Increasing defeat risk due to high risk equipment under pressure.", debug_enabled=debug)

    # Traversal Exposure Bias (TOWER-ENGINE-090)
    if trav_used:
        if rou_e > 0.6 and enemy_pressure > 0.5:
            effective_pressure += 0.1
            traversal_bias_reasoning.append("High route exposure increased environmental hazard.")
        
        if esc_r > 0.7 and player_health < 50:
            effective_pressure += 0.1
            traversal_bias_reasoning.append("High escape risk increased combat vulnerability.")

    # Room Route Specific Bias (TOWER-ENGINE-097)
    if route_used:
        # Route exposure increases general hazard
        if route_exp > 0.5:
            effective_pressure += (route_exp * 0.15)
            room_route_bias_reasoning.append(f"Route exposure ({route_exp:.2f}) increased combat friction.")
        
        # Environmental Profile Biases
        if env_profile:
            # High enemy exposure on route makes combat harder
            if env_profile.get("enemy_exposure", 0.0) > 0.6 and enemy_pressure > 0.4:
                effective_pressure += 0.1
                room_route_bias_reasoning.append("High local enemy density increased defeat risk.")
            
            # Darkness increases uncertainty
            if env_profile.get("darkness", 0.0) > 0.7:
                effective_pressure += 0.05
                room_route_bias_reasoning.append("Low visibility increased environmental hazard.")

        # Escape Modifier influence
        if esc_mod < -0.2:
             effective_pressure += 0.1
             room_route_bias_reasoning.append("Constricted route increased danger of being cornered.")

    if player_health <= 0:
        outcome = "DEFEAT_DROP"
    elif effective_pressure >= 0.90 and player_health < 25:
        outcome = "DEFEAT_DROP"
    elif (potions_used >= 25 or (trav_used and esc_r > 0.8 and potions_used > 10) or (route_used and esc_mod < -0.5 and potions_used > 5)) and effective_pressure > 0.60:
        # High escape risk or hazardous route biases retreat earlier (TOWER-ENGINE-090/097)
        outcome = "RETREAT_TO_HUB"
        if trav_used and esc_r > 0.8:
             traversal_bias_reasoning.append("Forced retreat due to unsustainable escape risk.")
        if route_used and esc_mod < -0.5:
             room_route_bias_reasoning.append("Forced retreat due to route constriction.")
    elif eq_used and eq_pressure.get("capacity_pressure", 0.0) > 0.8 and potions_used > 15:
        # High capacity pressure (heavy load) biases retreat if resources are low
        outcome = "RETREAT_TO_HUB"
        _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "DEBUG", "CapacityRetreatBias", "Retreating due to high capacity pressure and resource usage.", debug_enabled=debug)
    elif route_used and esc_mod > 0.2 and potions_used > 20:
        # Recovery/Escape routes support retreating earlier/safer (TOWER-ENGINE-097)
        outcome = "RETREAT_TO_HUB"
        room_route_bias_reasoning.append("Route topology supported a tactical retreat.")
    elif effective_pressure <= 0.75 and player_health > 0:
        outcome = "VICTORY_ASCEND"
    else:
        outcome = "VICTORY_ASCEND"

    combat_session["predicted_outcome"] = outcome
    
    # Apply Durability Decay (TOWER-ENGINE-077)
    durability_decay_applied = False
    durability_events = []
    updated_loadout = None
    
    if eq_used and eq_loadout:
        decay_res = durability_decay_stub.apply_loadout_durability_decay(
            eq_loadout, source='combat_pressure', 
            combat_pressure=enemy_pressure, capacity_pressure=capacity_p, 
            debug=debug
        )
        if decay_res["ok"]:
            durability_decay_applied = True
            durability_events = decay_res["durability_events"]
            updated_loadout = decay_res["equipment_loadout"]
            _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "INFO", "DurabilityDecayed", f"Applied decay to {len(durability_events)} items.", debug_enabled=debug)

    # Observe pressure
    resource_pressure_observed = potions_used > 10
    residue_pressure_observed = combat_session["residue_pressure"]["dominant_build_visibility"] > 0.5
    
    # Equipment-driven observations
    repair_pressure_observed = False
    eq_visibility_observed = False
    eq_affinity_observed = False
    durability_pressure_observed = durability_decay_applied

    if eq_used:
        if eq_pressure.get("repair_pressure", 0.0) > 0.5:
            repair_pressure_observed = True
            resource_pressure_observed = True # Equipment maintenance increases resource pressure
        
        if eq_pressure.get("residue_visibility", 0.0) > 0.6:
            eq_visibility_observed = True
            residue_pressure_observed = True # Equipment visibility increases total residue visibility
            
        if eq_pressure.get("mutation_affinity", 0.0) > 0.5:
            eq_affinity_observed = True

    # Traversal-driven observations (TOWER-ENGINE-090)
    if trav_used:
        if trav_p > 0.5:
            resource_pressure_observed = True
            traversal_bias_reasoning.append("High traversal pressure increased resource consumption.")

    # Room-Route-driven observations (TOWER-ENGINE-097)
    if route_used:
        if env_profile:
            if env_profile.get("resource_drain", 0.0) > 0.6:
                resource_pressure_observed = True
                room_route_bias_reasoning.append("Harsh environment increased resource drain.")
            if env_profile.get("mutation_scarring", 0.0) > 0.6:
                residue_pressure_observed = True
                room_route_bias_reasoning.append("Path instability increased residue visibility.")

    # Profile specific observations
    if archetype_id == "attrition_unit":
        resource_pressure_observed = True
    if archetype_id == "counter_unit":
        residue_pressure_observed = True

    result = {
        "ok": True,
        "combat_session": combat_session,
        "resolved_outcome": outcome,
        "pipeline_result": None,
        "resource_pressure_observed": resource_pressure_observed,
        "residue_pressure_observed": residue_pressure_observed,
        "enemy_archetype_id": archetype_id,
        "enemy_pressure_profile_used": profile is not None,
        "enemy_adaptation_reasoning": combat_session.get("enemy_adaptation_reasoning", []),
        "equipment_pressure_used": eq_used,
        "equipment_pressure": eq_pressure,
        "repair_pressure_observed": repair_pressure_observed,
        "equipment_residue_visibility_observed": eq_visibility_observed,
        "equipment_mutation_affinity_observed": eq_affinity_observed,
        "durability_decay_applied": durability_decay_applied,
        "durability_events": durability_events,
        "updated_equipment_loadout": updated_loadout,
        "durability_pressure_observed": durability_pressure_observed,
        "traversal_pressure_used": trav_used,
        "traversal_pressure": trav_p,
        "escape_risk": esc_r,
        "route_exposure": rou_e,
        "traversal_bias_reasoning": traversal_bias_reasoning,
        "room_route_bias_used": route_used,
        "selected_route_id": selected_route.get("route_id") if selected_route else None,
        "selected_route_type": selected_route.get("route_type") if selected_route else None,
        "route_exposure": route_exp,
        "environmental_profile": env_profile,
        "escape_modifier": esc_mod,
        "room_route_bias_reasoning": room_route_bias_reasoning,
        "error": None
    }

    _log_debug_event("TOWER-ENGINE-090", "combat_resolution_stub", "INFO", "ResolutionComplete", f"Combat resolved to {outcome}.", {"outcome": outcome}, debug)
    return result


def resolve_combat_into_pipeline(tower_state, combat_session, debug=False):
    """
    Resolves combat and feeds the outcome into the existing MVP outcome pipeline.
    """
    if not _dependencies_available:
        return {"ok": False, "error": "Outcome pipeline not available."}

    resolution = resolve_combat_session(combat_session, debug=debug)
    if not resolution["ok"]:
        return resolution

    outcome = resolution["resolved_outcome"]
    pipeline_result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(tower_state, outcome, debug=debug)
    
    resolution["pipeline_result"] = pipeline_result
    if not pipeline_result["ok"]:
        resolution["ok"] = False
        resolution["error"] = pipeline_result.get("error")

    return resolution
