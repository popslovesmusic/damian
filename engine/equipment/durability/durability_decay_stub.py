import os
import json
import uuid
import datetime
import copy

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

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_ITEM_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/equipment/contracts/equipment_item.schema.json")
_EVENT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/equipment/durability/contracts/durability_decay_event.schema.json")

PATCH_ID = "TOWER-ENGINE-076"
SYSTEM_NAME = "durability_decay_stub"

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

def calculate_durability_loss(equipment_item, combat_pressure=0.0, capacity_pressure=0.0, debug=False):
    """
    Deterministic durability loss calculation.
    """
    if not equipment_item or not isinstance(equipment_item, dict):
        return 0

    profile = equipment_item.get("operational_profile", {})
    repair_pressure = profile.get("repair_pressure", 0.0)
    mutation_affinity = profile.get("mutation_affinity", 0.0)
    
    # Base loss of 1 if any pressure exists
    total_pressure = combat_pressure + repair_pressure + mutation_affinity + capacity_pressure
    
    if total_pressure <= 0:
        return 0

    # Deterministic formula
    loss = 1.0 
    loss += combat_pressure * 8.0
    loss += repair_pressure * 4.0
    loss += mutation_affinity * 2.0
    loss += capacity_pressure * 2.0
    
    # Ensure it's at least 1 if meaningful pressure exists
    return int(max(1, round(loss)))

def apply_durability_decay(equipment_item, source='combat_pressure', combat_pressure=0.0, capacity_pressure=0.0, debug=False):
    """
    Applies durability decay to a copy of an equipment item.
    Returns structured success result with the updated item and decay event.
    """
    if not equipment_item or not isinstance(equipment_item, dict):
        return {"ok": False, "error": "InvalidItem", "message": "Equipment item missing or invalid."}

    new_item = copy.deepcopy(equipment_item)
    durability = new_item.get("durability", {})
    current = durability.get("current", 0)
    maximum = durability.get("maximum", 1)

    if current <= 0:
        _log_debug_event("INFO", "DecaySkipped", f"Item {new_item.get('equipment_item_id')} has 0 durability.", debug_enabled=debug)
        # Return success but with 0 loss
        event = _make_decay_event(new_item, source, 0, current, current, maximum, combat_pressure, capacity_pressure)
        return {
            "ok": True,
            "equipment_item": new_item,
            "durability_event": event,
            "summary": summarize_durability_decay(event),
            "error": None
        }

    loss = calculate_durability_loss(new_item, combat_pressure, capacity_pressure, debug=debug)
    
    # Apply loss with clamp
    new_current = max(0, current - loss)
    actual_loss = current - new_current
    
    durability["current"] = new_current
    
    event = _make_decay_event(new_item, source, actual_loss, current, new_current, maximum, combat_pressure, capacity_pressure)
    
    _log_debug_event("INFO", "DecayApplied", f"Item {new_item.get('equipment_item_id')} lost {actual_loss} durability.", {"event_id": event["event_id"]}, debug)
    
    return {
        "ok": True,
        "equipment_item": new_item,
        "durability_event": event,
        "summary": summarize_durability_decay(event),
        "error": None
    }

def apply_loadout_durability_decay(equipment_loadout, source='combat_pressure', combat_pressure=0.0, capacity_pressure=0.0, debug=False):
    """
    Applies durability decay to all items in an equipment loadout.
    Returns a structured result with updated loadout and list of events.
    """
    if not equipment_loadout or not isinstance(equipment_loadout, dict):
        return {"ok": False, "error": "InvalidLoadout", "message": "Loadout missing or invalid."}

    new_loadout = copy.deepcopy(equipment_loadout)
    items = new_loadout.get("equipped_items", [])
    events = []
    
    updated_items = []
    for item in items:
        res = apply_durability_decay(item, source, combat_pressure, capacity_pressure, debug=debug)
        if res["ok"]:
            updated_items.append(res["equipment_item"])
            events.append(res["durability_event"])
        else:
            updated_items.append(item) # Keep original if failed

    new_loadout["equipped_items"] = updated_items
    
    return {
        "ok": True,
        "equipment_loadout": new_loadout,
        "durability_events": events,
        "error": None
    }

def _make_decay_event(item, source, loss, before, after, maximum, combat_p, capacity_p):
    """Internal helper to build DurabilityDecayEvent record."""
    profile = item.get("operational_profile", {})
    return {
        "event_id": f"decay_{uuid.uuid4()}",
        "equipment_item_id": item.get("equipment_item_id", "unknown"),
        "source": source,
        "durability_before": before,
        "durability_after": after,
        "maximum_durability": maximum,
        "durability_loss": loss,
        "decay_pressure": {
            "combat_pressure": combat_p,
            "repair_pressure": profile.get("repair_pressure", 0.0),
            "mutation_affinity": profile.get("mutation_affinity", 0.0),
            "capacity_pressure": capacity_p
        },
        "bounded_flags_clean": True
    }

def validate_durability_decay_event(event, schema_path=None, debug=False):
    """Validates a decay event against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _EVENT_SCHEMA_PATH
    return json_save_manager.validate_json(event, schema_path, debug=debug)

def summarize_durability_decay(event):
    """Returns a human-readable summary of the decay event."""
    if not event:
        return "No decay event."
    
    return f"Durability Decay ({event.get('source')}): {event.get('equipment_item_id')} lost {event.get('durability_loss')} points. Remaining: {event.get('durability_after')}/{event.get('maximum_durability')}"
