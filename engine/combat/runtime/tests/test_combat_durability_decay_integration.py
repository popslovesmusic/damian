import pytest
import os
import json
from engine.combat.runtime import mvp_combat_resolution_stub
from engine.equipment.runtime import equipment_pressure_stub
from engine.equipment.durability import durability_decay_stub

def test_combat_session_with_loadout_and_capacity():
    """Validates that a combat session correctly includes loadout and capacity pressure."""
    player_state = {"player_id": "p1", "health": 100}
    item = {
        "equipment_item_id": "i1",
        "item_name": "Nail",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {"capacity_pressure": 0.5},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, equipment_loadout=loadout)
    
    assert session["equipment_loadout"] == loadout
    assert session["capacity_pressure"] == 0.5

def test_resolve_combat_applies_durability_decay():
    """Validates that resolving combat applies decay to the loadout."""
    player_state = {"player_id": "p1", "health": 100}
    item = {
        "equipment_item_id": "sword_01",
        "item_name": "Test Sword",
        "durability": {"current": 100, "maximum": 100},
        "operational_profile": {"repair_pressure": 0.1, "mutation_affinity": 0.1},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    # High enemy pressure to ensure decay
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, enemy_pressure_rating=0.8, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    assert result["durability_decay_applied"] is True
    assert len(result["durability_events"]) == 1
    assert result["durability_pressure_observed"] is True
    
    updated_item = result["updated_equipment_loadout"]["equipped_items"][0]
    assert updated_item["durability"]["current"] < 100
    assert updated_item["equipment_item_id"] == "sword_01"

def test_durability_decay_clamped_at_zero():
    """Validates that items don't go below 0 durability in combat."""
    player_state = {"player_id": "p1", "health": 100}
    item = {
        "equipment_item_id": "fragile_ring",
        "item_name": "Fragile Ring",
        "durability": {"current": 1, "maximum": 10},
        "operational_profile": {"repair_pressure": 0.9},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, enemy_pressure_rating=1.0, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    updated_item = result["updated_equipment_loadout"]["equipped_items"][0]
    assert updated_item["durability"]["current"] == 0

def test_resolve_combat_into_pipeline_preserves_decay():
    """Validates that pipeline resolution includes the decay data."""
    tower_state = {"current_floor": 1, "floor_memory": []}
    player_state = {"player_id": "p1", "health": 100}
    item = {
        "equipment_item_id": "i1",
        "item_name": "i1",
        "durability": {"current": 50, "maximum": 100},
        "operational_profile": {},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, session)
    
    assert result["durability_decay_applied"] is True
    assert result["updated_equipment_loadout"] is not None
    assert "pipeline_result" in result
    assert result["pipeline_result"]["ok"] is True

def test_debug_safety():
    """Validates that debug=True doesn't break integration."""
    player_state = {"player_id": "p1", "health": 100}
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, debug=True)
    mvp_combat_resolution_stub.resolve_combat_session(session, debug=True)
