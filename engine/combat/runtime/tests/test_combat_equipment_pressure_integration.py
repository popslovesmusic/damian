import pytest
import os
import json
from engine.combat.runtime import mvp_combat_resolution_stub
from engine.equipment.runtime import equipment_pressure_stub

def test_combat_session_with_equipment_loadout():
    """Validates that a combat session can be created with an equipment loadout."""
    player_state = {"player_id": "p1", "health": 100}
    item = {
        "equipment_item_id": "sword_01",
        "item_name": "Rusty Sword",
        "operational_profile": {"repair_pressure": 0.2, "residue_visibility": 0.3, "mutation_affinity": 0.1, "capacity_pressure": 0.1, "risk_profile": 0.2},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, equipment_loadout=loadout)
    
    assert session["equipment_loadout"] == loadout
    assert session["equipment_pressure_used"] is True
    assert session["equipment_pressure"]["repair_pressure"] == 0.2

def test_repair_pressure_influences_resource_pressure():
    """Validates that high repair pressure sets resource_pressure_observed."""
    player_state = {"player_id": "p1", "health": 100}
    # High repair pressure item
    item = {
        "operational_profile": {"repair_pressure": 0.8, "residue_visibility": 0.1, "mutation_affinity": 0.1, "capacity_pressure": 0.1, "risk_profile": 0.1},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    assert result["repair_pressure_observed"] is True
    assert result["resource_pressure_observed"] is True

def test_visibility_influences_residue_pressure():
    """Validates that high visibility sets residue_pressure_observed."""
    player_state = {"player_id": "p1", "health": 100}
    # High visibility item
    item = {
        "operational_profile": {"repair_pressure": 0.1, "residue_visibility": 0.9, "mutation_affinity": 0.1, "capacity_pressure": 0.1, "risk_profile": 0.1},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    assert result["equipment_residue_visibility_observed"] is True
    assert result["residue_pressure_observed"] is True

def test_capacity_pressure_biases_retreat():
    """Validates that high capacity pressure and high resource use bias retreat."""
    player_state = {"player_id": "p1", "health": 100}
    # High capacity pressure item
    item = {
        "operational_profile": {"repair_pressure": 0.1, "residue_visibility": 0.1, "mutation_affinity": 0.1, "capacity_pressure": 0.9, "risk_profile": 0.1},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    # Moderately high enemy pressure and moderate resource use
    session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.65, 
        resource_usage={"potions_used": 20}, equipment_loadout=loadout
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    assert result["resolved_outcome"] == "RETREAT_TO_HUB"

def test_risk_profile_increases_defeat_risk():
    """Validates that high risk profile gear increases defeat risk under pressure."""
    player_state = {"player_id": "p1", "health": 24} # Borderline health
    # High risk item
    item = {
        "operational_profile": {"repair_pressure": 0.1, "residue_visibility": 0.1, "mutation_affinity": 0.1, "capacity_pressure": 0.1, "risk_profile": 0.9},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    # High enemy pressure
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, enemy_pressure_rating=0.7, equipment_loadout=loadout)
    
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    # 0.7 enemy pressure + 0.15 risk bias = 0.85 (effectively pushes it towards defeat threshold if health is low)
    # The logic is effective_pressure >= 0.90 and health < 25 -> DEFEAT
    # Wait, my logic was effective_pressure += 0.15. 0.7 + 0.15 = 0.85. Still < 0.9.
    # Let's use enemy_pressure = 0.8. 0.8 + 0.15 = 0.95.
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state, enemy_pressure_rating=0.8, equipment_loadout=loadout)
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    
    assert result["resolved_outcome"] == "DEFEAT_DROP"

def test_resolve_combat_into_pipeline_preservation():
    """Validates that outcomes still route through the pipeline."""
    tower_state = {"current_floor": 1, "floor_memory": []}
    player_state = {"player_id": "p1", "health": 100}
    session = mvp_combat_resolution_stub.make_combat_session(1, player_state)
    
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, session)
    
    assert "pipeline_result" in result
    assert result["pipeline_result"]["ok"] is True
    assert "tower_state" in result["pipeline_result"]
