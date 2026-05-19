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


def make_combat_session(floor_id, player_state, enemy_pressure_rating=0.25, resource_usage=None, enemy_pressure_profile=None, debug=False):
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
        "enemy_adaptation_reasoning": enemy_pressure_profile.get("adaptation_reasoning", []) if enemy_pressure_profile else []
    }

    _log_debug_event("TOWER-ENGINE-048", "combat_resolution_stub", "INFO", "SessionCreated", f"Combat session created for floor {floor_id}.", {"session_id": combat_session["combat_session_id"]}, debug)
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
    _log_debug_event("TOWER-ENGINE-048", "combat_resolution_stub", "INFO", "ResolutionStart", "Resolving combat session.", {"session_id": combat_session["combat_session_id"]}, debug)

    player_health = combat_session["player_stats"].get("health", 0)
    enemy_pressure = combat_session["enemy_pressure_rating"]
    potions_used = combat_session["resource_usage"].get("potions_used", 0)
    profile = combat_session.get("enemy_pressure_profile")
    archetype_id = profile.get("enemy_archetype_id") if profile else None

    outcome = "VICTORY_ASCEND" # Default

    # Apply archetype biases to outcome
    effective_pressure = enemy_pressure
    if archetype_id == "ambush_unit" and player_health < 40:
        # Ambush units are more lethal at low health
        effective_pressure += 0.2
        _log_debug_event("TOWER-ENGINE-048", "combat_resolution_stub", "DEBUG", "AmbushBias", "Increasing defeat risk due to ambush unit at low health.", debug_enabled=debug)

    if player_health <= 0:
        outcome = "DEFEAT_DROP"
    elif effective_pressure >= 0.90 and player_health < 25:
        outcome = "DEFEAT_DROP"
    elif potions_used >= 25 and effective_pressure > 0.60:
        outcome = "RETREAT_TO_HUB"
    elif effective_pressure <= 0.75 and player_health > 0:
        outcome = "VICTORY_ASCEND"
    else:
        # Catch-all fallback
        outcome = "VICTORY_ASCEND"

    combat_session["predicted_outcome"] = outcome
    
    # Observe pressure
    resource_pressure_observed = potions_used > 10
    residue_pressure_observed = combat_session["residue_pressure"]["dominant_build_visibility"] > 0.5
    
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
        "error": None
    }

    _log_debug_event("TOWER-ENGINE-048", "combat_resolution_stub", "INFO", "ResolutionComplete", f"Combat resolved to {outcome}.", {"outcome": outcome}, debug)
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
