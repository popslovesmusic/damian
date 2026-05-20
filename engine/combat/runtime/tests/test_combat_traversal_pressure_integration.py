import pytest
import os
import json
from engine.combat.runtime import mvp_combat_resolution_stub

def test_combat_resolution_uses_traversal_pressure():
    """Validates that traversal pressure is used in combat resolution."""
    player_state = {"health": 100}
    traversal_summary = {
        "traversal_pressure": 0.8,
        "escape_risk": 0.5,
        "route_exposure": 0.2
    }
    
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, traversal_pressure_summary=traversal_summary
    )
    
    assert combat_session["traversal_pressure_used"] is True
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["traversal_pressure_used"] is True
    assert result["traversal_pressure"] == 0.8
    assert "resource consumption" in " ".join(result["traversal_bias_reasoning"])

def test_high_escape_risk_biases_retreat():
    """Validates that high escape risk pushes combat toward retreat."""
    player_state = {"health": 80}
    # High escape risk, moderate enemy pressure
    traversal_summary = {
        "traversal_pressure": 0.5,
        "escape_risk": 0.9,
        "route_exposure": 0.1
    }
    
    # Normally 0.7 enemy pressure and 15 potions doesn't force retreat (retreat > 25 potions or heavy load)
    # But now 0.9 escape risk + 15 potions should force it.
    resource_usage = {"potions_used": 15}
    
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.7, 
        resource_usage=resource_usage, traversal_pressure_summary=traversal_summary
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["resolved_outcome"] == "RETREAT_TO_HUB"
    assert "forced retreat" in " ".join(result["traversal_bias_reasoning"]).lower()

def test_high_route_exposure_biases_defeat():
    """Validates that high route exposure increases effective pressure/defeat risk."""
    player_state = {"health": 20} # Low health
    # High route exposure
    traversal_summary = {
        "traversal_pressure": 0.5,
        "escape_risk": 0.4,
        "route_exposure": 0.8
    }
    
    # 0.8 enemy pressure normally wouldn't defeat (needs 0.9 if health < 25)
    # But 0.8 + 0.1 (route bias) = 0.9
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.8, 
        traversal_pressure_summary=traversal_summary
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["resolved_outcome"] == "DEFEAT_DROP"
    assert "environmental hazard" in " ".join(result["traversal_bias_reasoning"])

def test_resolve_into_pipeline_preserves_mutation():
    """Validates that integrated combat still triggers mutations on defeat."""
    # We need a tower_state dictionary with complete floor memory (TOWER-ENGINE-090)
    tower_state = {
        "current_floor": 2,
        "floor_memory": [
            {
                "floor_id": 1, 
                "active_mutations": [], 
                "residue_history": [],
                "mutation_level": 0,
                "stability": 1.0,
                "deviation": 0.0,
                "visit_count": 0,
                "known_layout_seed": "seed1",
                "death_count": 0,
                "victory_count": 0,
                "discovered_easter_eggs": [],
                "unclaimed_easter_eggs": []
            },
            {
                "floor_id": 2, 
                "active_mutations": [], 
                "residue_history": [],
                "mutation_level": 0,
                "stability": 1.0,
                "deviation": 0.0,
                "visit_count": 0,
                "known_layout_seed": "seed2",
                "death_count": 0,
                "victory_count": 0,
                "discovered_easter_eggs": [],
                "unclaimed_easter_eggs": []
            }
        ]
    }
    
    # Force defeat
    player_state = {"health": 0}
    combat_session = mvp_combat_resolution_stub.make_combat_session(2, player_state)
    
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, combat_session)
    
    assert result["resolved_outcome"] == "DEFEAT_DROP"
    assert result["pipeline_result"]["mutation_applied"] is True
    # Floor should have dropped
    assert result["pipeline_result"]["current_floor"] == 1

def test_debug_safety():
    """Validates that debug=True doesn't break integration."""
    player_state = {"health": 100}
    traversal_summary = {"traversal_pressure": 0.5, "escape_risk": 0.5, "route_exposure": 0.5}
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, traversal_pressure_summary=traversal_summary, debug=True
    )
    mvp_combat_resolution_stub.resolve_combat_session(combat_session, debug=True)
