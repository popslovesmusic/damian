import pytest
import os
import json
from engine.traversal.runtime import traversal_pressure_stub

def test_calculate_traversal_pressure_deterministic():
    """Validates that traversal pressure calculation is deterministic."""
    p1 = traversal_pressure_stub.calculate_traversal_pressure(0.5, 0.5, 0.5, 0.5)
    p2 = traversal_pressure_stub.calculate_traversal_pressure(0.5, 0.5, 0.5, 0.5)
    assert p1 == p2
    assert 0.0 <= p1 <= 1.0

def test_pressure_influence():
    """Validates that each input factor influences the final pressure."""
    base = traversal_pressure_stub.calculate_traversal_pressure(0.1, 0.1, 0.1, 0.1)
    
    # Increase capacity
    with_cap = traversal_pressure_stub.calculate_traversal_pressure(0.9, 0.1, 0.1, 0.1)
    assert with_cap > base
    
    # Increase mutation
    with_mut = traversal_pressure_stub.calculate_traversal_pressure(0.1, 0.9, 0.1, 0.1)
    assert with_mut > base
    
    # Increase combat
    with_comb = traversal_pressure_stub.calculate_traversal_pressure(0.1, 0.1, 0.9, 0.1)
    assert with_comb > base
    
    # Increase repair
    with_rep = traversal_pressure_stub.calculate_traversal_pressure(0.1, 0.1, 0.1, 0.9)
    assert with_rep > base

def test_calculate_escape_risk_bounds():
    """Validates that escape risk remains between 0.0 and 1.0."""
    # Min
    assert traversal_pressure_stub.calculate_escape_risk(0.0, 0.0) == 0.0
    # Max
    assert traversal_pressure_stub.calculate_escape_risk(1.0, 1.0) == 1.0
    # Mixed
    risk = traversal_pressure_stub.calculate_escape_risk(0.5, 0.5)
    assert 0.0 <= risk <= 1.0

def test_make_traversal_event_schema_compatible():
    """Validates that created events match the traversal_event schema."""
    result = traversal_pressure_stub.make_traversal_event(
        "p1", "floor_01", "floor_02", "advance", 
        {"combat_exposure": 0.5, "mutation_pressure": 0.2}
    )
    assert result["ok"] is True
    event = result["traversal_event"]
    
    validation = traversal_pressure_stub.validate_traversal_event(event)
    assert validation["ok"] is True
    assert event["traversal_type"] == "advance"
    assert event["source_floor_id"] == "floor_01"

def test_make_traversal_event_with_inventory_state():
    """Validates that inventory state is used to calculate capacity pressure."""
    # Mock inventory state
    inventory = {"used_capacity": 20, "inventory_capacity": 40} # 0.5 pressure
    
    result = traversal_pressure_stub.make_traversal_event(
        "p1", "f1", "f2", pressure_inputs={"inventory_state": inventory}
    )
    assert result["ok"] is True
    assert result["traversal_event"]["traversal_pressure"]["capacity_pressure"] == 0.5

def test_invalid_traversal_type_fails_safely():
    """Validates safe failure for invalid traversal types."""
    result = traversal_pressure_stub.make_traversal_event("p1", "f1", "f2", traversal_type="teleport")
    assert result["ok"] is False
    assert result["error"] == "InvalidTraversalType"

def test_summarize_traversal_event():
    """Validates human-readable summary."""
    event = {
        "traversal_type": "advance",
        "source_floor_id": "f1",
        "destination_floor_id": "f2",
        "escape_risk": 0.45,
        "traversal_pressure": {"capacity_pressure": 0.2, "mutation_pressure": 0.3}
    }
    summary = traversal_pressure_stub.summarize_traversal_event(event)
    assert "advance" in summary
    assert "f1 -> f2" in summary
    assert "Risk: 0.45" in summary

def test_debug_safety():
    """Validates that debug=True doesn't break logic."""
    traversal_pressure_stub.calculate_traversal_pressure(0.5, debug=True)
    traversal_pressure_stub.make_traversal_event("p1", "f1", "f2", debug=True)
