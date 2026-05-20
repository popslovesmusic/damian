import pytest
import os
import json
from engine.inventory.runtime import inventory_transaction_stub

def test_make_default_inventory_state():
    """Validates default inventory state creation and schema compatibility."""
    state = inventory_transaction_stub.make_default_inventory_state()
    assert state["player_id"] == "player_default_001"
    assert "currency" in state
    assert state["currency"]["gold"] == 0.0
    assert state["items"] == []
    assert state["inventory_capacity"] == 40
    
    validation = inventory_transaction_stub.validate_inventory_state(state)
    assert validation["ok"] is True

def test_add_loot_to_inventory():
    """Validates adding loot (gold and materials) to inventory."""
    state = inventory_transaction_stub.make_default_inventory_state()
    loot_event = {
        "rewards": {
            "gold": 1000,
            "stability_shards": 1
        }
    }
    
    result = inventory_transaction_stub.add_loot_to_inventory(state, loot_event)
    assert result["ok"] is True
    new_state = result["inventory_state"]
    assert new_state["currency"]["gold"] == 1000
    assert new_state["currency"]["stability_shards"] == 1
    
    # Check original state wasn't modified
    assert state["currency"]["gold"] == 0

def test_consume_inventory_item_success():
    """Validates consuming an item from inventory."""
    state = inventory_transaction_stub.make_default_inventory_state()
    # Manually add item for test
    state["items"].append({"item_id": "potion", "quantity": 5, "capacity_cost": 1})
    state["used_capacity"] = 5
    
    result = inventory_transaction_stub.consume_inventory_item(state, "potion", 2)
    assert result["ok"] is True
    new_state = result["inventory_state"]
    assert len(new_state["items"]) == 1
    assert new_state["items"][0]["quantity"] == 3
    assert new_state["used_capacity"] == 3

def test_consume_inventory_item_removal():
    """Validates item is removed when quantity reaches zero."""
    state = inventory_transaction_stub.make_default_inventory_state()
    state["items"].append({"item_id": "potion", "quantity": 1, "capacity_cost": 1})
    state["used_capacity"] = 1
    
    result = inventory_transaction_stub.consume_inventory_item(state, "potion", 1)
    assert result["ok"] is True
    assert len(result["inventory_state"]["items"]) == 0
    assert result["inventory_state"]["used_capacity"] == 0

def test_consume_inventory_item_fail_missing():
    """Validates safe failure when item is missing."""
    state = inventory_transaction_stub.make_default_inventory_state()
    result = inventory_transaction_stub.consume_inventory_item(state, "potion", 1)
    assert result["ok"] is False
    assert "not found" in result["error"]["message"]
    # State should be original
    assert result["inventory_state"] == state

def test_consume_inventory_item_fail_insufficient():
    """Validates safe failure when quantity is insufficient."""
    state = inventory_transaction_stub.make_default_inventory_state()
    state["items"].append({"item_id": "potion", "quantity": 1, "capacity_cost": 1})
    
    result = inventory_transaction_stub.consume_inventory_item(state, "potion", 5)
    assert result["ok"] is False
    assert "Insufficient quantity" in result["error"]["message"]

def test_deduct_inventory_currency_success():
    """Validates deducting currency from inventory."""
    state = inventory_transaction_stub.make_default_inventory_state()
    state["currency"]["gold"] = 500
    
    result = inventory_transaction_stub.deduct_inventory_currency(state, {"gold": 200})
    assert result["ok"] is True
    assert result["inventory_state"]["currency"]["gold"] == 300

def test_deduct_inventory_currency_fail_insufficient():
    """Validates safe failure when currency is insufficient."""
    state = inventory_transaction_stub.make_default_inventory_state()
    state["currency"]["gold"] = 100
    
    result = inventory_transaction_stub.deduct_inventory_currency(state, {"gold": 200})
    assert result["ok"] is False
    assert "Insufficient gold" in result["error"]["message"]

def test_capacity_check_enforcement():
    """Validates that transactions fail if capacity is exceeded."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=10)
    
    # Try to add more than 10 items
    request = {
        "transaction_type": "ADD_LOOT",
        "items": [{"item_id": "heavy_rock", "quantity": 15, "capacity_cost": 1}]
    }
    
    result = inventory_transaction_stub.apply_inventory_transaction(state, request)
    assert result["ok"] is False
    assert "capacity exceeded" in result["error"]["message"]

def test_transaction_schema_validation():
    """Validates that transactions match the transaction schema."""
    state = inventory_transaction_stub.make_default_inventory_state()
    result = inventory_transaction_stub.add_loot_to_inventory(state, {"rewards": {"gold": 100}})
    
    tx = result["transaction"]
    validation = inventory_transaction_stub.validate_inventory_transaction(tx)
    assert validation["ok"] is True

def test_summarize_inventory_state():
    """Validates human-readable summary."""
    state = inventory_transaction_stub.make_default_inventory_state()
    state["currency"]["gold"] = 1234
    summary = inventory_transaction_stub.summarize_inventory_state(state)
    assert summary["gold"] == 1234
    assert "0/40" in summary["capacity"]

def test_debug_safety():
    """Validates that debug=True doesn't break functions."""
    state = inventory_transaction_stub.make_default_inventory_state(debug=True)
    inventory_transaction_stub.add_loot_to_inventory(state, {"rewards": {"gold": 10}}, debug=True)
    inventory_transaction_stub.check_inventory_capacity(state, debug=True)
