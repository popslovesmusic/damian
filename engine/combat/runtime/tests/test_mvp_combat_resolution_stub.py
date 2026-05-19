import os
import json
import pytest
import datetime
from engine.combat.runtime import mvp_combat_resolution_stub

@pytest.fixture
def mock_player_state():
    return {
        "player_id": "player_test_001",
        "health": 100.0,
        "damage": 10.0,
        "defense": 5.0,
        "speed": 1.0,
        "recovery": 0.5
    }

@pytest.fixture
def mock_tower_state():
    return {
        "tower_state_id": "tower_test_001",
        "engine_version": "0.0.1",
        "content_pack_id": "damian",
        "current_floor": 1,
        "highest_floor_reached": 1,
        "total_runs": 0,
        "total_deaths": 0,
        "last_outcome": "NONE",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "global_residue": {},
        "floor_memory": []
    }

def test_make_combat_session(mock_player_state):
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    assert session["floor_id"] == 1
    assert session["player_id"] == "player_test_001"
    assert "combat_session_id" in session
    assert session["player_stats"]["health"] == 100.0

def test_validate_combat_session(mock_player_state):
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    result = mvp_combat_resolution_stub.validate_combat_session(session)
    assert result["ok"] is True

def test_resolve_victory_ascend(mock_player_state):
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state, enemy_pressure_rating=0.25)
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    assert result["ok"] is True
    assert result["resolved_outcome"] == "VICTORY_ASCEND"

def test_resolve_defeat_drop_zero_health(mock_player_state):
    mock_player_state["health"] = 0
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    assert result["ok"] is True
    assert result["resolved_outcome"] == "DEFEAT_DROP"

def test_resolve_defeat_drop_high_pressure(mock_player_state):
    mock_player_state["health"] = 20
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state, enemy_pressure_rating=0.95)
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    assert result["ok"] is True
    assert result["resolved_outcome"] == "DEFEAT_DROP"

def test_resolve_retreat_to_hub(mock_player_state):
    resource_usage = {
        "potions_used": 30,
        "repair_items_used": 0,
        "recovery_events": 0
    }
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state, enemy_pressure_rating=0.70, resource_usage=resource_usage)
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    assert result["ok"] is True
    assert result["resolved_outcome"] == "RETREAT_TO_HUB"
    assert result["resource_pressure_observed"] is True

def test_resolve_combat_into_pipeline(mock_tower_state, mock_player_state):
    # Test victory flow
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(mock_tower_state, session)
    
    assert result["ok"] is True
    assert result["resolved_outcome"] == "VICTORY_ASCEND"
    assert result["pipeline_result"]["ok"] is True
    assert result["pipeline_result"]["current_floor"] == 2

def test_resolve_defeat_triggers_mutation(mock_tower_state, mock_player_state):
    mock_player_state["health"] = 0
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(mock_tower_state, session)
    
    assert result["ok"] is True
    assert result["resolved_outcome"] == "DEFEAT_DROP"
    assert result["pipeline_result"]["mutation_applied"] is True
    assert result["pipeline_result"]["survivor_mark_attached"] is True

def test_residue_pressure_observation(mock_player_state):
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state)
    session["residue_pressure"]["dominant_build_visibility"] = 0.8
    result = mvp_combat_resolution_stub.resolve_combat_session(session)
    assert result["residue_pressure_observed"] is True

def test_debug_mode_safe(mock_tower_state, mock_player_state):
    session = mvp_combat_resolution_stub.make_combat_session(1, mock_player_state, debug=True)
    result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(mock_tower_state, session, debug=True)
    assert result["ok"] is True
