import pytest
import os
import json
from engine.inventory.runtime import inventory_transaction_stub

def test_add_loot_reports_capacity_pressure():
    """Validates that add_loot transaction reports capacity pressure."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=40)
    # Add an item that takes space
    request = {
        "transaction_type": "ADD_LOOT",
        "items": [{"item_id": "iron_ore", "quantity": 10, "capacity_cost": 1}]
    }
    
    result = inventory_transaction_stub.apply_inventory_transaction(state, request)
    assert result["ok"] is True
    assert "capacity_pressure_summary" in result
    assert result["capacity_pressure_summary"]["capacity_pressure"] == 0.25
    assert result["capacity_pressure_summary"]["capacity_band"] == "LOW"

def test_consume_item_reports_updated_capacity_pressure():
    """Validates that consume transaction reports updated capacity pressure."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=40)
    state["items"].append({"item_id": "potion", "quantity": 20, "capacity_cost": 1})
    state["used_capacity"] = 20
    
    result = inventory_transaction_stub.consume_inventory_item(state, "potion", 10)
    assert result["ok"] is True
    # 10/40 = 0.25
    assert result["capacity_pressure_summary"]["capacity_pressure"] == 0.25
    assert result["summary"]["capacity_band"] == "LOW"

def test_currency_deduction_reports_unchanged_capacity_pressure():
    """Validates that currency deduction reports unchanged capacity pressure."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=40)
    state["items"].append({"item_id": "sword", "quantity": 1, "capacity_cost": 10})
    state["used_capacity"] = 10
    state["currency"]["gold"] = 1000
    
    result = inventory_transaction_stub.deduct_inventory_currency(state, {"gold": 500})
    assert result["ok"] is True
    # 10/40 = 0.25
    assert result["capacity_pressure_summary"]["capacity_pressure"] == 0.25

def test_failed_transaction_reports_pre_transaction_pressure():
    """Validates that failed transactions report original capacity pressure."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=40)
    state["items"].append({"item_id": "sword", "quantity": 1, "capacity_cost": 10})
    state["used_capacity"] = 10
    
    # Fail due to insufficient gold
    result = inventory_transaction_stub.deduct_inventory_currency(state, {"gold": 500})
    assert result["ok"] is False
    assert result["capacity_pressure_summary"]["capacity_pressure"] == 0.25
    # Ensure original state untouched
    assert result["inventory_state"]["used_capacity"] == 10

def test_over_capacity_add_fails_safely():
    """Validates that adding items beyond capacity fails safely."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=10)
    
    request = {
        "transaction_type": "ADD_LOOT",
        "items": [{"item_id": "rock", "quantity": 15, "capacity_cost": 1}]
    }
    
    result = inventory_transaction_stub.apply_inventory_transaction(state, request)
    assert result["ok"] is False
    assert result["capacity_pressure_summary"]["capacity_pressure"] == 0.0
    assert result["inventory_state"]["items"] == []

def test_summarize_inventory_state_includes_capacity_data():
    """Validates that summarize_inventory_state includes pressure and band."""
    state = inventory_transaction_stub.make_default_inventory_state(inventory_capacity=40)
    state["used_capacity"] = 30 # HIGH band (> 0.6 and < 1.0)
    
    summary = inventory_transaction_stub.summarize_inventory_state(state)
    assert summary["capacity_pressure"] == 0.75
    assert summary["capacity_band"] == "HIGH"

def test_debug_mode_safety():
    """Validates that debug=True doesn't break capacity integration."""
    state = inventory_transaction_stub.make_default_inventory_state()
    inventory_transaction_stub.add_loot_to_inventory(state, {"rewards": {"gold": 10}}, debug=True)
    inventory_transaction_stub.check_inventory_capacity(state, debug=True)
