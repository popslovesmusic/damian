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

# Import inventory systems
try:
    from engine.inventory.runtime import inventory_transaction_stub
    _inventory_available = True
except ImportError:
    _inventory_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_REPAIR_EVENT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/equipment/repair/contracts/repair_event.schema.json")

PATCH_ID = "TOWER-ENGINE-081"
SYSTEM_NAME = "repair_runtime_stub"

# Bounded repair rules
REPAIR_MATERIAL_ID = "repair_material_basic"
DURABILITY_PER_MATERIAL = 10.0

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

def calculate_repair_amount(equipment_item, material_quantity=1, debug=False):
    """
    Calculates the amount of durability that would be restored.
    """
    if material_quantity < 1:
        return 0.0
    
    return float(material_quantity * DURABILITY_PER_MATERIAL)

def make_repair_event(equipment_item, inventory_state, material_quantity=1, debug=False):
    """
    Creates a RepairEvent record for an attempted repair.
    This does NOT apply the repair.
    """
    durability = equipment_item.get("durability", {})
    before = durability.get("current", 0)
    maximum = durability.get("maximum", 1)
    
    amount = calculate_repair_amount(equipment_item, material_quantity, debug=debug)
    after = min(maximum, before + amount)
    restored = after - before

    event = {
        "repair_event_id": f"repair_{uuid.uuid4()}",
        "equipment_item_id": equipment_item.get("equipment_item_id", "unknown"),
        "inventory_id": inventory_state.get("inventory_id", "unknown"),
        "player_id": inventory_state.get("player_id", "player_default"),
        "materials_required": [
            {"item_id": REPAIR_MATERIAL_ID, "quantity": material_quantity}
        ],
        "materials_consumed": [], # Populated on success
        "durability_before": before,
        "durability_after": after,
        "maximum_durability": maximum,
        "durability_restored": restored,
        "repair_applied": False,
        "failure_reason": None,
        "bounded_flags_clean": True
    }
    return event

def apply_repair(equipment_item, inventory_state, material_quantity=1, debug=False):
    """
    Executes a repair by consuming materials and updating equipment durability.
    Returns a structured result containing the updated state and the event record.
    """
    if not equipment_item or not inventory_state:
        return {"ok": False, "error": "InvalidArguments", "message": "Item or inventory missing."}

    # 1. Prepare event record
    event = make_repair_event(equipment_item, inventory_state, material_quantity, debug=debug)
    
    if event["durability_restored"] <= 0 and equipment_item["durability"]["current"] >= equipment_item["durability"]["maximum"]:
        _log_debug_event("INFO", "RepairSkipped", "Item already at maximum durability.", debug_enabled=debug)
        event["failure_reason"] = "Item already at maximum durability."
        return {
            "ok": True, 
            "equipment_item": equipment_item, 
            "inventory_state": inventory_state,
            "repair_event": event,
            "inventory_transaction": None,
            "summary": summarize_repair_event(event),
            "error": None
        }

    # 2. Attempt material deduction via inventory stub
    if not _inventory_available:
        return {"ok": False, "error": "DependencyError", "message": "inventory_transaction_stub unavailable."}

    inv_res = inventory_transaction_stub.consume_inventory_item(
        inventory_state, REPAIR_MATERIAL_ID, quantity=material_quantity, debug=debug
    )

    if not inv_res["ok"]:
        _log_debug_event("WARNING", "RepairFailed", f"Insufficient materials: {inv_res['error']['message']}", debug_enabled=debug)
        event["failure_reason"] = inv_res["error"]["message"]
        return {
            "ok": False,
            "equipment_item": equipment_item,
            "inventory_state": inventory_state,
            "repair_event": event,
            "inventory_transaction": inv_res.get("transaction"),
            "summary": summarize_repair_event(event),
            "error": inv_res["error"]
        }

    # 3. Apply changes to a copy of the equipment item
    new_item = copy.deepcopy(equipment_item)
    new_item["durability"]["current"] = event["durability_after"]
    
    # 4. Finalize event
    event["repair_applied"] = True
    event["materials_consumed"] = event["materials_required"]
    
    _log_debug_event("INFO", "RepairSuccess", f"Item {new_item.get('equipment_item_id')} repaired. Restored {event['durability_restored']}.", {"event_id": event["repair_event_id"]}, debug)

    return {
        "ok": True,
        "equipment_item": new_item,
        "inventory_state": inv_res["inventory_state"],
        "repair_event": event,
        "inventory_transaction": inv_res["transaction"],
        "summary": summarize_repair_event(event),
        "error": None
    }

def validate_repair_event(repair_event, schema_path=None, debug=False):
    """Validates a repair event against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _REPAIR_EVENT_SCHEMA_PATH
    return json_save_manager.validate_json(repair_event, schema_path, debug=debug)

def summarize_repair_event(repair_event):
    """Returns a human-readable summary of the repair event."""
    if not repair_event:
        return "No repair event."
    
    if not repair_event.get("repair_applied"):
        return f"Repair Failed: {repair_event.get('failure_reason', 'Unknown reason')}"

    return f"Repair Success: {repair_event.get('equipment_item_id')} restored {repair_event.get('durability_restored')} durability using {repair_event.get('materials_consumed')[0]['quantity']} materials."
