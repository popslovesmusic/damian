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
    from engine.inventory.runtime import inventory_capacity_pressure
    _capacity_available = True
except ImportError:
    _capacity_available = False

# Paths to inventory schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_STATE_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/inventory/runtime/contracts/inventory_state.schema.json")
_ITEM_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/inventory/runtime/contracts/inventory_item.schema.json")
_TRANSACTION_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/inventory/runtime/contracts/inventory_transaction.schema.json")

PATCH_ID = "TOWER-ENGINE-071"
SYSTEM_NAME = "inventory_transaction_stub"

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

def make_default_inventory_state(player_id='player_default_001', inventory_capacity=40, debug=False):
    """
    Creates a default schema-compatible inventory state.
    """
    state = {
        "inventory_id": f"inv_{uuid.uuid4()}",
        "player_id": player_id,
        "items": [],
        "currency": {
            "gold": 0.0,
            "domain_essence": 0.0,
            "stability_shards": 0.0,
            "residue_fragments": 0.0,
            "rare_materials": 0.0
        },
        "inventory_capacity": inventory_capacity,
        "used_capacity": 0,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    _log_debug_event("INFO", "StateCreated", f"Default inventory state created for {player_id}.", {"inventory_id": state["inventory_id"]}, debug)
    return state

def calculate_used_capacity(items):
    """Calculates used capacity from items list."""
    total = 0
    for item in items:
        # Default capacity cost is 1 if not specified
        cost = item.get("capacity_cost", 1)
        total += cost * item.get("quantity", 1)
    return total

def apply_inventory_transaction(inventory_state, transaction_request, debug=False):
    """
    Applies a transaction request to a copy of the inventory state.
    Returns a structured result with the new state or an error.
    """
    new_state = copy.deepcopy(inventory_state)
    transaction_id = f"tx_{uuid.uuid4()}"
    tx_type = transaction_request.get("transaction_type", "FAILED_SAFE")
    
    # Initialize transaction record
    transaction = {
        "transaction_id": transaction_id,
        "inventory_id": new_state["inventory_id"],
        "player_id": new_state["player_id"],
        "transaction_type": tx_type,
        "items_added": [],
        "items_deducted": [],
        "currency_delta": {
            "gold": 0, "domain_essence": 0, "stability_shards": 0, 
            "residue_fragments": 0, "rare_materials": 0
        },
        "capacity_before": new_state["used_capacity"],
        "capacity_after": new_state["used_capacity"],
        "inventory_capacity": new_state["inventory_capacity"],
        "transaction_applied": False,
        "failure_reason": None,
        "bounded_flags_clean": True
    }

    try:
        if tx_type == "ADD_LOOT":
            loot = transaction_request.get("loot_event", {})
            rewards = loot.get("rewards", {})
            
            # Apply currency
            for curr, val in rewards.items():
                if curr in new_state["currency"]:
                    new_state["currency"][curr] += val
                    transaction["currency_delta"][curr] = val
            
            # Apply items if any
            items = transaction_request.get("items")
            if items is None:
                items = loot.get("items", [])
            
            for item in items:
                existing = next((i for i in new_state["items"] if i["item_id"] == item["item_id"]), None)
                if existing:
                    existing["quantity"] += item["quantity"]
                else:
                    new_state["items"].append(copy.deepcopy(item))
                transaction["items_added"].append(item)

        elif tx_type == "CONSUME_ITEM":
            item_id = transaction_request.get("item_id")
            qty = transaction_request.get("quantity", 1)
            
            existing = next((i for i in new_state["items"] if i["item_id"] == item_id), None)
            if not existing:
                raise ValueError(f"Item {item_id} not found in inventory.")
            if existing["quantity"] < qty:
                raise ValueError(f"Insufficient quantity for {item_id}.")
            
            existing["quantity"] -= qty
            if existing["quantity"] == 0:
                new_state["items"].remove(existing)
            transaction["items_deducted"].append({"item_id": item_id, "quantity": qty})

        elif tx_type == "DEDUCT_CURRENCY":
            delta = transaction_request.get("currency_delta", {})
            for curr, val in delta.items():
                if curr not in new_state["currency"]:
                    continue
                if new_state["currency"][curr] < val:
                    raise ValueError(f"Insufficient {curr}.")
                new_state["currency"][curr] -= val
                transaction["currency_delta"][curr] = -val

        elif tx_type == "CAPACITY_CHECK":
            pass
        
        else:
            raise ValueError(f"Invalid transaction type: {tx_type}")

        # Recalculate and verify capacity
        new_state["used_capacity"] = calculate_used_capacity(new_state["items"])
        transaction["capacity_after"] = new_state["used_capacity"]
        
        if new_state["used_capacity"] > new_state["inventory_capacity"]:
            raise ValueError(f"Inventory capacity exceeded: {new_state['used_capacity']}/{new_state['inventory_capacity']}")

        new_state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        transaction["transaction_applied"] = True

        # Calculate capacity pressure summary (TOWER-ENGINE-071)
        cap_summary = None
        if _capacity_available:
            cap_summary = inventory_capacity_pressure.summarize_capacity_pressure(new_state, debug=debug)

        return {
            "ok": True,
            "inventory_state": new_state,
            "transaction": transaction,
            "summary": summarize_inventory_state(new_state, debug=debug),
            "capacity_pressure_summary": cap_summary,
            "error": None
        }

    except Exception as e:
        transaction["failure_reason"] = str(e)
        _log_debug_event("ERROR", "TransactionFailed", str(e), {"tx_type": tx_type}, debug)

        # Calculate capacity pressure for original state on failure
        cap_summary = None
        if _capacity_available:
            cap_summary = inventory_capacity_pressure.summarize_capacity_pressure(inventory_state, debug=debug)

        return {
            "ok": False,
            "inventory_state": inventory_state, # Return original
            "transaction": transaction,
            "summary": summarize_inventory_state(inventory_state, debug=debug),
            "capacity_pressure_summary": cap_summary,
            "error": {"message": str(e), "type": "TransactionError"}
        }

def add_loot_to_inventory(inventory_state, loot_event, debug=False):
    """Wrapper for ADD_LOOT transaction."""
    request = {"transaction_type": "ADD_LOOT", "loot_event": loot_event}
    return apply_inventory_transaction(inventory_state, request, debug=debug)

def consume_inventory_item(inventory_state, item_id, quantity=1, debug=False):
    """Wrapper for CONSUME_ITEM transaction."""
    request = {"transaction_type": "CONSUME_ITEM", "item_id": item_id, "quantity": quantity}
    return apply_inventory_transaction(inventory_state, request, debug=debug)

def deduct_inventory_currency(inventory_state, currency_delta, debug=False):
    """Wrapper for DEDUCT_CURRENCY transaction."""
    request = {"transaction_type": "DEDUCT_CURRENCY", "currency_delta": currency_delta}
    return apply_inventory_transaction(inventory_state, request, debug=debug)

def check_inventory_capacity(inventory_state, debug=False):
    """Wrapper for CAPACITY_CHECK transaction."""
    request = {"transaction_type": "CAPACITY_CHECK"}
    return apply_inventory_transaction(inventory_state, request, debug=debug)

def validate_inventory_state(inventory_state, schema_path=None, debug=False):
    """Validates inventory state against schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _STATE_SCHEMA_PATH
    return json_save_manager.validate_json(inventory_state, schema_path, debug=debug)

def validate_inventory_transaction(transaction, schema_path=None, debug=False):
    """Validates inventory transaction against schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _TRANSACTION_SCHEMA_PATH
    return json_save_manager.validate_json(transaction, schema_path, debug=debug)

def summarize_inventory_state(inventory_state, debug=False):
    """Returns a human-readable summary of the inventory including capacity pressure."""
    if not inventory_state:
        return "No inventory state."
    
    curr = inventory_state.get("currency", {})
    summary = {
        "gold": curr.get("gold", 0),
        "items_count": len(inventory_state.get("items", [])),
        "capacity": f"{inventory_state.get('used_capacity')}/{inventory_state.get('inventory_capacity')}"
    }

    # Integrate capacity pressure (TOWER-ENGINE-071)
    if _capacity_available:
        inventory_capacity_pressure.apply_capacity_pressure_to_inventory_summary(inventory_state, summary, debug=debug)

    return summary
