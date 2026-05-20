import pytest
import os
import json
from engine.traversal.runtime import traversal_pressure_stub

def test_calculate_traversal_pressure_with_route_exposure():
    """Validates that route exposure influences aggregate traversal pressure."""
    # Base case (all inputs zero)
    base = traversal_pressure_stub.calculate_traversal_pressure()
    
    # With high route exposure
    with_route = traversal_pressure_stub.calculate_traversal_pressure(route_exposure=0.8)
    assert with_route > base
    # Check weight (0.8 * 0.2 = 0.16)
    assert with_route == 0.16

def test_calculate_traversal_pressure_with_env_profile():
    """Validates that environmental profile (darkness, instability) biases pressure."""
    base = traversal_pressure_stub.calculate_traversal_pressure(route_exposure=0.5)
    
    # Add dark/unstable profile
    profile = {"darkness": 0.9, "instability": 0.8}
    with_env = traversal_pressure_stub.calculate_traversal_pressure(route_exposure=0.5, environmental_profile=profile)
    
    assert with_env > base
    # (0.5 * 0.2) + (0.9 * 0.1) + (0.8 * 0.1) = 0.1 + 0.09 + 0.08 = 0.27
    assert with_env == 0.27

def test_calculate_escape_risk_with_modifier():
    """Validates that escape modifiers materially influence risk."""
    tp = 0.5
    re = 0.5
    base_risk = traversal_pressure_stub.calculate_escape_risk(tp, re) # 0.5
    
    # Positive modifier (Safety/Recovery) lowers risk
    safe_risk = traversal_pressure_stub.calculate_escape_risk(tp, re, escape_modifier=0.2)
    assert safe_risk < base_risk
    assert safe_risk == 0.3
    
    # Negative modifier (Pressure/Hazard) raises risk
    hazard_risk = traversal_pressure_stub.calculate_escape_risk(tp, re, escape_modifier=-0.2)
    assert hazard_risk > base_risk
    assert hazard_risk == 0.7

def test_make_traversal_event_with_route_evidence():
    """Validates that traversal events capture route identity and hazards."""
    route = {
        "route_id": "r1",
        "route_type": "pressure_route",
        "environmental_profile": {"darkness": 0.5, "instability": 0.5},
        "escape_modifier": -0.1,
        "route_exposure": 0.7
    }
    
    result = traversal_pressure_stub.make_traversal_event(
        "p1", "f1", "f2", traversal_type="advance", route=route
    )
    
    assert result["ok"] is True
    event = result["traversal_event"]
    assert event["route_id"] == "r1"
    assert event["route_type"] == "pressure_route"
    assert event["route_pressure_used"] is True
    assert event["escape_modifier"] == -0.1
    assert "environmental_profile" in event
    
    # Verify risk calculation used modifier
    # tp = (0.7 * 0.2) + (0.5 * 0.1) + (0.5 * 0.1) = 0.14 + 0.05 + 0.05 = 0.24
    # risk = (0.24 * 0.7) + (0.7 * 0.3) - (-0.1) = 0.168 + 0.21 + 0.1 = 0.478
    assert event["escape_risk"] == 0.478

def test_traversal_pressure_bounds_with_route():
    """Validates that aggregate hazards remain strictly bounded."""
    profile = {"darkness": 1.0, "instability": 1.0}
    p = traversal_pressure_stub.calculate_traversal_pressure(1, 1, 1, 1, 1, profile)
    assert 0.0 <= p <= 1.0
    
    r = traversal_pressure_stub.calculate_escape_risk(1, 1, -1.0)
    assert 0.0 <= r <= 1.0

def test_summarize_traversal_event_with_route():
    """Validates human-readable summary for route-aware events."""
    route = {"route_id": "r1", "route_type": "side_route", "route_exposure": 0.4}
    res = traversal_pressure_stub.make_traversal_event("p1", "f1", "f2", route=route)
    summary = traversal_pressure_stub.summarize_traversal_event(res["traversal_event"])
    
    assert "Route r1 (side_route)" in summary
    assert "f1 -> f2" in summary
