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

# Import json_save_manager for validation
try:
    from engine.save.runtime import json_save_manager
    _save_manager_available = True
except ImportError:
    _save_manager_available = False

# Path to loot event schema
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_LOOT_EVENT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/loot/contracts/loot_event.schema.json")

PATCH_ID = "TOWER-ENGINE-052"
SYSTEM_NAME = "loot_event_stub"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass
    elif not _debug_logger_available and debug_enabled:
        print(f"DEBUG [{SYSTEM_NAME}]: {message}")

def make_loot_event(floor_id, source='combat_reward', outcome='VICTORY_ASCEND', debug=False):
    """
    Core function to create a bounded schema-compatible loot event.
    """
    if not isinstance(floor_id, int) or floor_id < 1:
        _log_debug_event("ERROR", "InvalidFloorId", f"Invalid floor_id: {floor_id}", debug_enabled=debug)
        return {"ok": False, "error": "InvalidFloorId", "message": f"Floor ID must be a positive integer, got {floor_id}"}

    # Bounded Reward Rules (TOWER-ENGINE-052 requirements)
    stub_data = {
        "VICTORY_ASCEND": {
            "gold": 10000,
            "stability_shards": 1,
            "residue_fragments": 1,
            "rare_materials": 0
        },
        "DEFEAT_DROP": {
            "gold": 1500,
            "stability_shards": 0,
            "residue_fragments": 1,
            "rare_materials": 0
        },
        "RETREAT_TO_HUB": {
            "gold": 500,
            "stability_shards": 0,
            "residue_fragments": 0,
            "rare_materials": 0
        },
        "survivor_mark_reward": {
            "gold": 2500,
            "stability_shards": 2,
            "residue_fragments": 1,
            "rare_materials": 1
        }
    }

    # Select rewards based on source and outcome
    if source == 'survivor_mark_reward':
        rewards_data = stub_data["survivor_mark_reward"]
        items_data = []
    else:
        rewards_data = stub_data.get(outcome, stub_data["RETREAT_TO_HUB"])
        # Give some basic repair materials on victory to test maintenance loop
        if outcome == "VICTORY_ASCEND":
            items_data = [{"item_id": "repair_material_basic", "quantity": 5, "capacity_cost": 1}]
        else:
            items_data = []

    # Resource Sink Pressure Defaults
    resource_sink_pressure = {
        "estimated_potion_cost": 250,
        "estimated_repair_cost": 120,
        "estimated_mutation_control_cost": 900,
        "estimated_domain_upkeep_cost": 1200
    }

    # Bounded Reward Flags (Must remain False per requirements)
    bounded_reward_flags = {
        "grants_invulnerability": False,
        "grants_infinite_damage": False,
        "bypasses_residue": False,
        "bypasses_death_consequence": False
    }

    loot_event = {
        "loot_event_id": f"loot_{uuid.uuid4()}",
        "floor_id": floor_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": source,
        "outcome": outcome if source == 'combat_reward' else "N/A",
        "rewards": rewards_data,
        "items": items_data,
        "resource_sink_pressure": resource_sink_pressure,
        "bounded_reward_flags": bounded_reward_flags
    }

    _log_debug_event("INFO", "LootEventCreated", f"Loot event created for floor {floor_id} from {source}.", {"loot_event_id": loot_event["loot_event_id"]}, debug)
    return {"ok": True, "payload": loot_event}

def make_combat_loot_event(floor_id, outcome='VICTORY_ASCEND', debug=False):
    """Wrapper for combat-specific loot events."""
    return make_loot_event(floor_id, source='combat_reward', outcome=outcome, debug=debug)

def make_survivor_mark_loot_event(floor_id, survivor_mark_id, debug=False):
    """Wrapper for survivor mark loot events."""
    result = make_loot_event(floor_id, source='survivor_mark_reward', debug=debug)
    if result["ok"]:
        result["payload"]["survivor_mark_id"] = survivor_mark_id
    return result

def validate_loot_event(loot_event, schema_path=None, debug=False):
    """Validates a loot event against the schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}

    if schema_path is None:
        schema_path = _LOOT_EVENT_SCHEMA_PATH

    return json_save_manager.validate_json(loot_event, schema_path, debug=debug)

def summarize_loot_event(loot_event):
    """Returns a human-readable summary of the loot event."""
    if not loot_event:
        return "No loot event available."
    
    rewards = loot_event.get("rewards", {})
    summary = f"Loot Event ({loot_event.get('source')}): "
    summary += f"Gold: {rewards.get('gold', 0)}, "
    summary += f"Shards: {rewards.get('stability_shards', 0)}, "
    summary += f"Fragments: {rewards.get('residue_fragments', 0)}, "
    summary += f"Materials: {rewards.get('rare_materials', 0)}"
    return summary
