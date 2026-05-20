import pytest
import os
import json
from engine.equipment.durability import durability_decay_stub

def test_calculate_durability_loss_deterministic():
    """Validates that loss calculation is deterministic."""
    item = {
        "operational_profile": {
            "repair_pressure": 0.5,
            "mutation_affinity": 0.2
        }
    }
    loss1 = durability_decay_stub.calculate_durability_loss(item, combat_pressure=0.6, capacity_pressure=0.3)
    loss2 = durability_decay_stub.calculate_durability_loss(item, combat_pressure=0.6, capacity_pressure=0.3)
    assert loss1 == loss2
    assert loss1 > 0

def test_apply_durability_decay_reduces_durability():
    """Validates that apply_durability_decay reduces durability correctly."""
    item = {
        "equipment_item_id": "sword_01",
        "item_name": "Test Sword",
        "durability": {"current": 100, "maximum": 100},
        "operational_profile": {"repair_pressure": 0.1, "mutation_affinity": 0.1}
    }
    result = durability_decay_stub.apply_durability_decay(item, combat_pressure=0.5)
    assert result["ok"] is True
    assert result["equipment_item"]["durability"]["current"] < 100
    assert result["durability_event"]["durability_loss"] > 0
    assert result["durability_event"]["durability_after"] == result["equipment_item"]["durability"]["current"]

def test_durability_never_drops_below_zero():
    """Validates that durability_after is clamped at 0."""
    item = {
        "durability": {"current": 2, "maximum": 100},
        "operational_profile": {"repair_pressure": 0.9, "mutation_affinity": 0.9}
    }
    # Force high loss
    result = durability_decay_stub.apply_durability_decay(item, combat_pressure=1.0, capacity_pressure=1.0)
    assert result["ok"] is True
    assert result["equipment_item"]["durability"]["current"] == 0
    assert result["durability_event"]["durability_after"] == 0
    assert result["durability_event"]["durability_loss"] == 2

def test_equipment_identity_preserved():
    """Validates that item ID and name are preserved after decay."""
    item = {
        "equipment_item_id": "unique_id_123",
        "item_name": "Relic of Old",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {"repair_pressure": 0.1, "mutation_affinity": 0.1}
    }
    result = durability_decay_stub.apply_durability_decay(item, combat_pressure=0.1)
    assert result["equipment_item"]["equipment_item_id"] == "unique_id_123"
    assert result["equipment_item"]["item_name"] == "Relic of Old"

def test_apply_loadout_durability_decay():
    """Validates that multiple items in a loadout are updated."""
    loadout = {
        "equipped_items": [
            {"equipment_item_id": "i1", "durability": {"current": 50, "maximum": 100}, "operational_profile": {}},
            {"equipment_item_id": "i2", "durability": {"current": 50, "maximum": 100}, "operational_profile": {}}
        ]
    }
    result = durability_decay_stub.apply_loadout_durability_decay(loadout, combat_pressure=0.5)
    assert result["ok"] is True
    assert len(result["durability_events"]) == 2
    assert result["equipment_loadout"]["equipped_items"][0]["durability"]["current"] < 50
    assert result["equipment_loadout"]["equipped_items"][1]["durability"]["current"] < 50

def test_zero_durability_safely_ignored():
    """Validates that items with 0 durability report 0 further loss."""
    item = {
        "equipment_item_id": "broken_pick",
        "durability": {"current": 0, "maximum": 100},
        "operational_profile": {"repair_pressure": 1.0}
    }
    result = durability_decay_stub.apply_durability_decay(item, combat_pressure=1.0)
    assert result["ok"] is True
    assert result["durability_event"]["durability_loss"] == 0
    assert result["durability_event"]["durability_after"] == 0

def test_summarize_durability_decay():
    """Validates human-readable summary."""
    event = {
        "source": "combat_pressure",
        "equipment_item_id": "ash_blade",
        "durability_loss": 5,
        "durability_after": 95,
        "maximum_durability": 100
    }
    summary = durability_decay_stub.summarize_durability_decay(event)
    assert "lost 5 points" in summary
    assert "95/100" in summary

def test_debug_safety():
    """Validates that debug=True doesn't break functions."""
    item = {"durability": {"current": 10, "maximum": 10}, "operational_profile": {}}
    durability_decay_stub.apply_durability_decay(item, debug=True)
