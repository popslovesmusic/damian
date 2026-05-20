import pytest
import os
import json
from engine.combat.runtime import mvp_combat_resolution_stub

def test_combat_resolution_uses_room_route_bias():
    """Validates that room routes are used for combat biasing."""
    player_state = {"health": 100}
    selected_route = {
        "route_id": "r1",
        "route_type": "side_route",
        "route_exposure": 0.8,
        "environmental_profile": {"enemy_exposure": 0.9}
    }
    
    # Use higher enemy pressure to trigger local density bias (threshold > 0.4)
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.5, selected_route=selected_route
    )
    
    assert combat_session["room_route_bias_used"] is True
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["room_route_bias_used"] is True
    assert result["selected_route_id"] == "r1"
    assert "Route exposure" in " ".join(result["room_route_bias_reasoning"])
    assert "enemy density" in " ".join(result["room_route_bias_reasoning"])

def test_high_resource_drain_sets_pressure_flag():
    """Validates that route resource drain increases resource pressure observed."""
    player_state = {"health": 100}
    selected_route = {
        "route_type": "pressure_route",
        "environmental_profile": {"resource_drain": 0.9}
    }
    
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, selected_route=selected_route
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["resource_pressure_observed"] is True
    assert "resource drain" in " ".join(result["room_route_bias_reasoning"])

def test_high_mutation_scarring_sets_residue_flag():
    """Validates that route instability increases residue pressure observed."""
    player_state = {"health": 100}
    selected_route = {
        "route_type": "survivor_mark_route",
        "environmental_profile": {"mutation_scarring": 0.9}
    }
    
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, selected_route=selected_route
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["residue_pressure_observed"] is True
    assert "residue visibility" in " ".join(result["room_route_bias_reasoning"])

def test_negative_escape_modifier_biases_defeat():
    """Validates that hazardous route modifiers increase danger."""
    player_state = {"health": 20} # Low health
    selected_route = {
        "route_type": "pressure_route",
        "escape_modifier": -0.8
    }
    
    # 0.8 enemy pressure normally wouldn't defeat (needs 0.9 if health < 25)
    # But -0.8 modifier adds 0.1 bias
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.8, selected_route=selected_route
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["resolved_outcome"] == "DEFEAT_DROP"
    assert "cornered" in " ".join(result["room_route_bias_reasoning"])

def test_recovery_route_supports_retreat():
    """Validates that safe routes support earlier tactical retreats."""
    player_state = {"health": 80}
    selected_route = {
        "route_type": "recovery_route",
        "escape_modifier": 0.5
    }
    
    # High resource usage (21 potions) + Recovery route should force retreat (threshold > 20)
    resource_usage = {"potions_used": 21}
    
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, enemy_pressure_rating=0.7, 
        resource_usage=resource_usage, selected_route=selected_route
    )
    
    result = mvp_combat_resolution_stub.resolve_combat_session(combat_session)
    assert result["resolved_outcome"] == "RETREAT_TO_HUB"
    assert "tactical retreat" in " ".join(result["room_route_bias_reasoning"])

def test_debug_safety():
    """Validates that debug=True doesn't break integration."""
    player_state = {"health": 100}
    selected_route = {"route_id": "r1", "route_exposure": 0.5}
    combat_session = mvp_combat_resolution_stub.make_combat_session(
        1, player_state, selected_route=selected_route, debug=True
    )
    mvp_combat_resolution_stub.resolve_combat_session(combat_session, debug=True)
