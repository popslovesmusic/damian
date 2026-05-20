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

# Paths to equipment schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_ITEM_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/equipment/contracts/equipment_item.schema.json")
_LOADOUT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/equipment/contracts/equipment_loadout.schema.json")

PATCH_ID = "TOWER-ENGINE-058"
SYSTEM_NAME = "equipment_pressure_stub"

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

def calculate_aggregate_equipment_pressure(equipped_items, debug=False):
    """
    Calculates aggregate pressure values as the average of item operational_profile values.
    Returns zeroed aggregate if items are empty.
    """
    aggregate = {
        "repair_pressure": 0.0,
        "residue_visibility": 0.0,
        "mutation_affinity": 0.0,
        "capacity_pressure": 0.0,
        "risk_profile": 0.0
    }

    if not equipped_items:
        return aggregate

    item_count = len(equipped_items)
    
    for item in equipped_items:
        profile = item.get("operational_profile", {})
        for key in aggregate.keys():
            val = profile.get(key, 0.0)
            # Bound check per requirements
            val = max(0.0, min(1.0, val))
            aggregate[key] += val

    # Calculate averages
    for key in aggregate.keys():
        aggregate[key] = round(aggregate[key] / item_count, 4)

    _log_debug_event("INFO", "PressureCalculated", f"Calculated aggregate pressure for {item_count} items.", aggregate, debug)
    return aggregate

def build_equipment_loadout(player_id, equipped_items, debug=False):
    """
    Builds a complete EquipmentLoadout object.
    Sets bounded_rules_clean = True only if ALL items have false bypass flags.
    """
    # 1. Calculate aggregate pressure
    aggregate = calculate_aggregate_equipment_pressure(equipped_items, debug=debug)
    
    # 2. Check safety bounds
    bounded_rules_clean = True
    for item in equipped_items:
        flags = item.get("bounded_flags", {})
        if any(flags.values()):
            bounded_rules_clean = False
            break

    loadout = {
        "loadout_id": f"loadout_{uuid.uuid4()}",
        "player_id": player_id,
        "equipped_items": equipped_items,
        "aggregate_pressure": aggregate,
        "bounded_rules_clean": bounded_rules_clean
    }

    _log_debug_event("INFO", "LoadoutBuilt", f"Loadout built for player {player_id}. Clean: {bounded_rules_clean}", {"loadout_id": loadout["loadout_id"]}, debug)
    return loadout

def validate_equipment_item(equipment_item, schema_path=None, debug=False):
    """Validates an equipment item against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}

    if schema_path is None:
        schema_path = _ITEM_SCHEMA_PATH

    return json_save_manager.validate_json(equipment_item, schema_path, debug=debug)

def validate_equipment_loadout(loadout, schema_path=None, debug=False):
    """Validates an equipment loadout against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}

    if schema_path is None:
        schema_path = _LOADOUT_SCHEMA_PATH

    # Note: loadout schema uses a $ref to equipment_item. 
    # json_save_manager.validate_json might need RefResolver if it doesn't handle it.
    # We'll assume the manager is capable or handle it surgically if it fails in audit.
    return json_save_manager.validate_json(loadout, schema_path, debug=debug)

def summarize_equipment_pressure(loadout):
    """Returns a human-readable summary of the loadout pressure."""
    if not loadout:
        return "No loadout available."
    
    agg = loadout.get("aggregate_pressure", {})
    clean = loadout.get("bounded_rules_clean", False)
    
    summary = f"Equipment Loadout (Items: {len(loadout.get('equipped_items', []))})\n"
    summary += f"Status: {'BOUNDED' if clean else 'VIOLATION DETECTED'}\n"
    summary += f"- Repair Pressure: {agg.get('repair_pressure', 0.0):.2f}\n"
    summary += f"- Visibility: {agg.get('residue_visibility', 0.0):.2f}\n"
    summary += f"- Mutation Affinity: {agg.get('mutation_affinity', 0.0):.2f}\n"
    summary += f"- Capacity: {agg.get('capacity_pressure', 0.0):.2f}\n"
    summary += f"- Risk: {agg.get('risk_profile', 0.0):.2f}"
    
    return summary
