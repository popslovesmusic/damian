import pytest
import os
import json
from engine.equipment.runtime import equipment_pressure_stub

def test_calculate_aggregate_pressure_empty():
    """Validates that empty items return zeroed aggregate pressure."""
    aggregate = equipment_pressure_stub.calculate_aggregate_equipment_pressure([])
    assert aggregate["repair_pressure"] == 0.0
    assert aggregate["residue_visibility"] == 0.0
    assert aggregate["mutation_affinity"] == 0.0
    assert aggregate["capacity_pressure"] == 0.0
    assert aggregate["risk_profile"] == 0.0

def test_calculate_aggregate_pressure_averaging():
    """Validates that aggregate pressure is an average of item profiles."""
    item1 = {
        "operational_profile": {
            "repair_pressure": 0.4,
            "residue_visibility": 0.6,
            "mutation_affinity": 0.2,
            "capacity_pressure": 0.2,
            "risk_profile": 0.5
        }
    }
    item2 = {
        "operational_profile": {
            "repair_pressure": 0.6,
            "residue_visibility": 0.4,
            "mutation_affinity": 0.8,
            "capacity_pressure": 0.4,
            "risk_profile": 0.5
        }
    }
    
    aggregate = equipment_pressure_stub.calculate_aggregate_equipment_pressure([item1, item2])
    
    assert aggregate["repair_pressure"] == 0.5
    assert aggregate["residue_visibility"] == 0.5
    assert aggregate["mutation_affinity"] == 0.5
    assert aggregate["capacity_pressure"] == 0.3
    assert aggregate["risk_profile"] == 0.5

def test_build_loadout_bounded_rules_clean():
    """Validates that bounded_rules_clean correctly reflects bypass flags."""
    clean_item = {
        "bounded_flags": {
            "grants_invulnerability": False,
            "grants_infinite_scaling": False,
            "bypasses_residue": False,
            "bypasses_defeat": False
        }
    }
    dirty_item = {
        "bounded_flags": {
            "grants_invulnerability": True,
            "grants_infinite_scaling": False,
            "bypasses_residue": False,
            "bypasses_defeat": False
        }
    }
    
    # Case 1: All clean
    loadout1 = equipment_pressure_stub.build_equipment_loadout("p1", [clean_item, clean_item])
    assert loadout1["bounded_rules_clean"] is True
    
    # Case 2: One dirty
    loadout2 = equipment_pressure_stub.build_equipment_loadout("p1", [clean_item, dirty_item])
    assert loadout2["bounded_rules_clean"] is False

def test_validate_equipment_item_schema():
    """Validates equipment item against schema."""
    item = {
        "equipment_item_id": "test_item_001",
        "item_name": "Test Blade",
        "category_id": "weapons",
        "rarity": "common",
        "durability": {"current": 10, "maximum": 10},
        "operational_profile": {
            "repair_pressure": 0.1,
            "residue_visibility": 0.1,
            "mutation_affinity": 0.1,
            "capacity_pressure": 0.1,
            "risk_profile": 0.1
        },
        "bounded_flags": {
            "grants_invulnerability": False,
            "grants_infinite_scaling": False,
            "bypasses_residue": False,
            "bypasses_defeat": False
        }
    }
    
    validation = equipment_pressure_stub.validate_equipment_item(item)
    assert validation["ok"] is True

def test_validate_equipment_loadout_schema():
    """Validates equipment loadout against schema."""
    item = {
        "equipment_item_id": "test_item_001",
        "item_name": "Test Blade",
        "category_id": "weapons",
        "rarity": "common",
        "durability": {"current": 10, "maximum": 10},
        "operational_profile": {
            "repair_pressure": 0.1,
            "residue_visibility": 0.1,
            "mutation_affinity": 0.1,
            "capacity_pressure": 0.1,
            "risk_profile": 0.1
        },
        "bounded_flags": {
            "grants_invulnerability": False,
            "grants_infinite_scaling": False,
            "bypasses_residue": False,
            "bypasses_defeat": False
        }
    }
    
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    
    validation = equipment_pressure_stub.validate_equipment_loadout(loadout)
    assert validation["ok"] is True

def test_summarize_equipment_pressure():
    """Validates human-readable summary."""
    item = {
        "operational_profile": {"repair_pressure": 0.5, "residue_visibility": 0.5, "mutation_affinity": 0.5, "capacity_pressure": 0.5, "risk_profile": 0.5},
        "bounded_flags": {"grants_invulnerability": False, "grants_infinite_scaling": False, "bypasses_residue": False, "bypasses_defeat": False}
    }
    loadout = equipment_pressure_stub.build_equipment_loadout("p1", [item])
    summary = equipment_pressure_stub.summarize_equipment_pressure(loadout)
    
    assert "BOUNDED" in summary
    assert "Repair Pressure: 0.50" in summary
    assert "Items: 1" in summary

def test_debug_logging_safe():
    """Validates that calculation doesn't break if debug is True."""
    # This just ensures no exception is raised
    equipment_pressure_stub.calculate_aggregate_equipment_pressure([], debug=True)
    equipment_pressure_stub.build_equipment_loadout("p1", [], debug=True)
