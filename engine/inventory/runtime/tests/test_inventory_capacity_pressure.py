import pytest
import os
import json
from engine.inventory.runtime import inventory_capacity_pressure

def test_calculate_capacity_pressure_empty():
    """Validates that empty inventory returns 0.0 pressure."""
    state = {"used_capacity": 0, "inventory_capacity": 40}
    pressure = inventory_capacity_pressure.calculate_capacity_pressure(state)
    assert pressure == 0.0

def test_calculate_capacity_pressure_full():
    """Validates that full inventory returns 1.0 pressure."""
    state = {"used_capacity": 40, "inventory_capacity": 40}
    pressure = inventory_capacity_pressure.calculate_capacity_pressure(state)
    assert pressure == 1.0

def test_calculate_capacity_pressure_clamping():
    """Validates that pressure is clamped between 0.0 and 1.0."""
    state_over = {"used_capacity": 50, "inventory_capacity": 40}
    pressure = inventory_capacity_pressure.calculate_capacity_pressure(state_over)
    assert pressure == 1.0
    
    state_under = {"used_capacity": -5, "inventory_capacity": 40}
    pressure = inventory_capacity_pressure.calculate_capacity_pressure(state_under)
    assert pressure == 0.0

def test_capacity_bands():
    """Validates that capacity bands are correctly assigned."""
    # EMPTY
    assert inventory_capacity_pressure.get_capacity_band(0.0) == "EMPTY"
    
    # LOW (<= 0.25)
    assert inventory_capacity_pressure.get_capacity_band(0.1) == "LOW"
    assert inventory_capacity_pressure.get_capacity_band(0.25) == "LOW"
    
    # MODERATE (<= 0.60)
    assert inventory_capacity_pressure.get_capacity_band(0.26) == "MODERATE"
    assert inventory_capacity_pressure.get_capacity_band(0.60) == "MODERATE"
    
    # HIGH (< 1.0)
    assert inventory_capacity_pressure.get_capacity_band(0.61) == "HIGH"
    assert inventory_capacity_pressure.get_capacity_band(0.99) == "HIGH"
    
    # FULL
    assert inventory_capacity_pressure.get_capacity_band(1.0) == "FULL"

def test_summarize_capacity_pressure_success():
    """Validates structured summary for valid state."""
    state = {"inventory_id": "inv_001", "used_capacity": 10, "inventory_capacity": 40}
    summary = inventory_capacity_pressure.summarize_capacity_pressure(state)
    
    assert summary["ok"] is True
    assert summary["capacity_pressure"] == 0.25
    assert summary["capacity_band"] == "LOW"
    assert summary["over_capacity"] is False

def test_summarize_capacity_pressure_over_capacity():
    """Validates summary for over-capacity state."""
    state = {"used_capacity": 41, "inventory_capacity": 40}
    summary = inventory_capacity_pressure.summarize_capacity_pressure(state)
    
    assert summary["ok"] is True
    assert summary["capacity_pressure"] == 1.0
    assert summary["over_capacity"] is True
    assert summary["capacity_band"] == "INVALID"

def test_invalid_inventory_capacity():
    """Validates safe failure for invalid capacity values."""
    # cap = 0
    state = {"used_capacity": 10, "inventory_capacity": 0}
    summary = inventory_capacity_pressure.summarize_capacity_pressure(state)
    assert summary["ok"] is False
    assert summary["capacity_band"] == "INVALID"
    
    # Missing state
    summary = inventory_capacity_pressure.summarize_capacity_pressure(None)
    assert summary["ok"] is False

def test_apply_capacity_pressure_to_summary():
    """Validates enrichment of existing summary."""
    state = {"used_capacity": 20, "inventory_capacity": 40}
    summary = {"existing_key": "val"}
    
    enriched = inventory_capacity_pressure.apply_capacity_pressure_to_inventory_summary(state, summary)
    
    assert enriched["existing_key"] == "val"
    assert enriched["capacity_band"] == "MODERATE"
    assert enriched["capacity_report"] == "20/40 (MODERATE)"

def test_debug_safety():
    """Validates that debug=True doesn't break logic."""
    state = {"used_capacity": 0, "inventory_capacity": 1}
    inventory_capacity_pressure.calculate_capacity_pressure(state, debug=True)
    inventory_capacity_pressure.summarize_capacity_pressure(state, debug=True)
