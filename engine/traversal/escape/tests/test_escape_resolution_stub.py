import pytest
import os
import json
import datetime
from engine.traversal.escape import escape_resolution_stub

@pytest.fixture
def mock_tower_state():
    return {
        "tower_state_id": "tower_test_001",
        "current_floor": 2,
        "floor_memory": [
            {
                "floor_id": 1, "active_mutations": [], "residue_history": [],
                "mutation_level": 0, "stability": 1.0, "deviation": 0.0,
                "visit_count": 0, "death_count": 0, "victory_count": 0,
                "known_layout_seed": "seed1", "discovered_easter_eggs": [], "unclaimed_easter_eggs": []
            },
            {
                "floor_id": 2, "active_mutations": [], "residue_history": [],
                "mutation_level": 0, "stability": 1.0, "deviation": 0.0,
                "visit_count": 0, "death_count": 0, "victory_count": 0,
                "known_layout_seed": "seed2", "discovered_easter_eggs": [], "unclaimed_easter_eggs": []
            }
        ]
    }

def test_resolve_escape_success():
    """Validates ESCAPE_SUCCESS outcome."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.2)
    assert res["ok"] is True
    er = res["escape_resolution"]
    assert er["outcome"] == "ESCAPE_SUCCESS"
    assert er["pipeline_outcome"] == "RETREAT_TO_HUB"
    assert er["residue_written"] is True

def test_resolve_escape_partial():
    """Validates ESCAPE_PARTIAL outcome."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.5)
    assert res["escape_resolution"]["outcome"] == "ESCAPE_PARTIAL"
    assert res["escape_resolution"]["resource_loss"]["gold"] == 100.0

def test_resolve_escape_pressure_spike():
    """Validates ESCAPE_FAILED_PRESSURE_SPIKE outcome."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.7)
    assert res["escape_resolution"]["outcome"] == "ESCAPE_FAILED_PRESSURE_SPIKE"
    assert res["escape_resolution"]["mutation_pressure_delta"] == 0.1

def test_resolve_escape_retreat_drop():
    """Validates ESCAPE_FAILED_RETREAT_DROP outcome (Severe failure)."""
    # High risk and high exposure
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.9, route_exposure=0.8)
    assert res["escape_resolution"]["outcome"] == "ESCAPE_FAILED_RETREAT_DROP"
    assert res["escape_resolution"]["pipeline_outcome"] == "DEFEAT_DROP"
    assert res["escape_resolution"]["mutation_pressure_delta"] == 0.2

def test_escape_resolution_schema_compatibility():
    """Validates created records against schema."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 1, escape_risk=0.5)
    validation = escape_resolution_stub.validate_escape_resolution(res["escape_resolution"])
    assert validation["ok"] is True

def test_resolve_into_pipeline_retreat(mock_tower_state):
    """Validates routing of success/partial to RETREAT_TO_HUB."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.2)
    pipe_res = escape_resolution_stub.resolve_escape_into_pipeline(mock_tower_state, res["escape_resolution"])
    assert pipe_res["ok"] is True
    assert pipe_res["pipeline_result"]["outcome"] == "RETREAT_TO_HUB"
    assert pipe_res["pipeline_result"]["current_floor"] == 0

def test_resolve_into_pipeline_defeat(mock_tower_state):
    """Validates routing of severe failure to DEFEAT_DROP."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.9, route_exposure=0.8)
    pipe_res = escape_resolution_stub.resolve_escape_into_pipeline(mock_tower_state, res["escape_resolution"])
    assert pipe_res["ok"] is True
    assert pipe_res["pipeline_result"]["outcome"] == "DEFEAT_DROP"
    assert pipe_res["pipeline_result"]["current_floor"] == 1
    assert pipe_res["pipeline_result"]["mutation_applied"] is True

def test_summarize_escape_resolution():
    """Validates human-readable summary."""
    res = escape_resolution_stub.resolve_escape_attempt("p1", 2, escape_risk=0.2)
    summary = escape_resolution_stub.summarize_escape_resolution(res["escape_resolution"])
    assert "Safe retreat" in summary

def test_debug_safety():
    """Validates that debug=True doesn't break logic."""
    escape_resolution_stub.resolve_escape_attempt("p1", 1, debug=True)
