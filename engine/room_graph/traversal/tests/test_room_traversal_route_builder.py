import pytest
import os
import json
from engine.room_graph.traversal import room_traversal_route_builder

@pytest.fixture
def mock_node_a():
    return {
        "node_id": "entry_a",
        "node_type": "entry_room",
        "difficulty_rating": 0.1,
        "stability": 1.0,
        "connections": ["combat_a"]
    }

@pytest.fixture
def mock_node_b():
    return {
        "node_id": "combat_a",
        "node_type": "combat_room",
        "difficulty_rating": 0.5,
        "stability": 0.8,
        "connections": ["exit_a"]
    }

def test_make_environmental_profile_deterministic(mock_node_a, mock_node_b):
    """Validates that profile generation is deterministic."""
    p1 = room_traversal_route_builder.make_environmental_profile("primary_route", mock_node_a, mock_node_b)
    p2 = room_traversal_route_builder.make_environmental_profile("primary_route", mock_node_a, mock_node_b)
    assert p1 == p2

def test_calculate_route_exposure_bounds():
    """Validates that route exposure remains between 0.0 and 1.0."""
    p_low = {"darkness": 0.0, "instability": 0.0, "enemy_exposure": 0.0, "resource_drain": 0.0, "mutation_scarring": 0.0}
    p_high = {"darkness": 1.0, "instability": 1.0, "enemy_exposure": 1.0, "resource_drain": 1.0, "mutation_scarring": 1.0}
    
    assert room_traversal_route_builder.calculate_route_exposure(p_low) == 0.0
    assert room_traversal_route_builder.calculate_route_exposure(p_high) == 1.0

def test_calculate_escape_modifier_bounds():
    """Validates that escape modifier remains between -1.0 and 1.0."""
    p = {"darkness": 1.0, "instability": 1.0}
    mod = room_traversal_route_builder.calculate_escape_modifier("pressure_route", p)
    assert -1.0 <= mod <= 1.0

def test_build_room_traversal_route_schema_compatible(mock_node_a, mock_node_b):
    """Validates that created routes match the room_traversal_route schema."""
    res = room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, "primary_route")
    assert res["ok"] is True
    route = res["route"]
    
    validation = room_traversal_route_builder.validate_room_traversal_route(route)
    assert validation["ok"] is True
    assert route["floor_id"] == 1
    assert route["critical_route"] is True

def test_build_routes_from_room_graph():
    """Validates route construction from a full room graph."""
    mock_graph = {
        "floor_id": 2,
        "mutation_level": 1,
        "nodes": [
            {"node_id": "n1", "node_type": "entry_room", "connections": ["n2"], "difficulty_rating": 0.1, "stability": 1.0},
            {"node_id": "n2", "node_type": "pressure_room", "connections": ["n3"], "difficulty_rating": 0.6, "stability": 0.7},
            {"node_id": "n3", "node_type": "exit_room", "connections": [], "difficulty_rating": 0.0, "stability": 1.0}
        ]
    }
    
    res = room_traversal_route_builder.build_routes_from_room_graph(mock_graph)
    assert res["ok"] is True
    assert len(res["routes"]) == 2
    
    # Check pressure route inference
    pressure_route = next((r for r in res["routes"] if r["to_node_id"] == "n2"), None)
    assert pressure_route["route_type"] == "pressure_route"
    assert pressure_route["critical_route"] is True

def test_route_type_specific_rules(mock_node_a, mock_node_b):
    """Validates route type specific flags and modifiers."""
    # Escape route
    res_esc = room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, "escape_route")
    assert res_esc["route"]["critical_route"] is False
    
    # Survivor mark route
    res_sm = room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, "survivor_mark_route")
    assert res_sm["route"]["supports_survivor_mark"] is True

def test_invalid_route_type_fails_safely(mock_node_a, mock_node_b):
    """Validates safe failure for unknown route types."""
    res = room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, "shortcut")
    assert res["ok"] is False
    assert res["error"] == "InvalidRouteType"

def test_summarize_room_traversal_route(mock_node_a, mock_node_b):
    """Validates human-readable summary."""
    res = room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, "primary_route")
    summary = room_traversal_route_builder.summarize_room_traversal_route(res["route"])
    assert "primary_route" in summary
    assert "entry_a -> combat_a" in summary

def test_debug_safety(mock_node_a, mock_node_b):
    """Validates that debug=True doesn't break logic."""
    room_traversal_route_builder.build_room_traversal_route(1, mock_node_a, mock_node_b, debug=True)
