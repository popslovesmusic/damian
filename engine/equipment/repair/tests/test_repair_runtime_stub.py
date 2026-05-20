import pytest
import os
import json
from engine.equipment.repair import repair_runtime_stub
from engine.inventory.runtime import inventory_transaction_stub

def test_calculate_repair_amount():
    """Validates that repair amount is calculated correctly."""
    item = {"durability": {"current": 50, "maximum": 100}}
    # 1 material = 10 durability
    amount = repair_runtime_stub.calculate_repair_amount(item, material_quantity=2)
    assert amount == 20.0

def test_apply_repair_success():
    """Validates successful repair with sufficient materials."""
    item = {
        "equipment_item_id": "sword_01",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    # Inventory with materials
    inventory = inventory_transaction_stub.make_default_inventory_state()
    inventory["items"].append({"item_id": "repair_material_basic", "quantity": 5, "capacity_cost": 1})
    
    result = repair_runtime_stub.apply_repair(item, inventory, material_quantity=2)
    
    assert result["ok"] is True
    assert result["equipment_item"]["durability"]["current"] == 70
    assert result["repair_event"]["repair_applied"] is True
    assert result["repair_event"]["durability_restored"] == 20
    
    # Check inventory deduction
    mat = next((i for i in result["inventory_state"]["items"] if i["item_id"] == "repair_material_basic"), None)
    assert mat["quantity"] == 3

def test_apply_repair_fail_insufficient_materials():
    """Validates safe failure when materials are insufficient."""
    item = {
        "equipment_item_id": "sword_01",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {}
    }
    inventory = inventory_transaction_stub.make_default_inventory_state()
    
    result = repair_runtime_stub.apply_repair(item, inventory, material_quantity=1)
    
    assert result["ok"] is False
    assert result["repair_event"]["repair_applied"] is False
    assert "not found" in result["error"]["message"]
    # Equipment and inventory should be unchanged
    assert result["equipment_item"] == item
    assert result["inventory_state"] == inventory

def test_apply_repair_prevents_over_repair():
    """Validates that repair does not exceed maximum durability."""
    item = {
        "equipment_item_id": "fragile_staff",
        "durability": {"current": 95, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {}
    }
    inventory = inventory_transaction_stub.make_default_inventory_state()
    inventory["items"].append({"item_id": "repair_material_basic", "quantity": 5, "capacity_cost": 1})
    
    # 1 material restores 10, but only 5 is needed
    result = repair_runtime_stub.apply_repair(item, inventory, material_quantity=1)
    
    assert result["ok"] is True
    assert result["equipment_item"]["durability"]["current"] == 100
    assert result["repair_event"]["durability_restored"] == 5

def test_equipment_identity_preserved():
    """Validates that item ID and name are preserved after repair."""
    item = {
        "equipment_item_id": "unique_relic",
        "item_name": "Relic of Old",
        "durability": {"current": 10, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    inventory = inventory_transaction_stub.make_default_inventory_state()
    inventory["items"].append({"item_id": "repair_material_basic", "quantity": 10})
    
    result = repair_runtime_stub.apply_repair(item, inventory, material_quantity=1)
    assert result["equipment_item"]["equipment_item_id"] == "unique_relic"
    assert result["equipment_item"]["item_name"] == "Relic of Old"

def test_validate_repair_event_schema():
    """Validates repair event against its schema."""
    item = {
        "equipment_item_id": "i1",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    inventory = inventory_transaction_stub.make_default_inventory_state()
    inventory["items"].append({"item_id": "repair_material_basic", "quantity": 5})
    
    result = repair_runtime_stub.apply_repair(item, inventory, material_quantity=1)
    event = result["repair_event"]
    
    validation = repair_runtime_stub.validate_repair_event(event)
    assert validation["ok"] is True

def test_summarize_repair_event():
    """Validates human-readable summary."""
    event = {
        "repair_applied": True,
        "equipment_item_id": "ash_blade",
        "durability_restored": 10,
        "materials_consumed": [{"item_id": "repair_material_basic", "quantity": 1}]
    }
    summary = repair_runtime_stub.summarize_repair_event(event)
    assert "Repair Success" in summary
    assert "restored 10 durability" in summary

def test_debug_safety():
    """Validates that debug=True doesn't break functions."""
    item = {"durability": {"current": 10, "maximum": 100}, "operational_profile": {}}
    inventory = inventory_transaction_stub.make_default_inventory_state()
    repair_runtime_stub.apply_repair(item, inventory, debug=True)
