import pytest
import os
import json
import datetime
from engine.dashboard.domain import domain_dashboard_snapshot_builder

@pytest.fixture
def mock_session_state():
    return {
        "runtime_context": {
            "tower_state": {
                "current_floor": 2,
                "floor_memory": [
                    {
                        "floor_id": 2,
                        "active_mutations": ["m1", "m2"],
                        "residue_history": ["r1", "r2", "r3"],
                        "unclaimed_easter_eggs": ["mark1"]
                    }
                ]
            },
            "player_progression": {
                "player_id": "test_player_1",
                "highest_floor_reached": 3
            }
        },
        "inventory_state": {
            "gold": 1250.0,
            "items": [
                {"item_id": "ash_potion_small", "quantity": 5},
                {"item_id": "repair_material_basic", "quantity": 3}
            ],
            "used_capacity": 20,
            "inventory_capacity": 40
        },
        "equipment_loadout": {
            "equipped_items": [
                {
                    "item_id": "sword_1",
                    "durability": {"current": 50, "maximum": 100}
                }
            ],
            "aggregate_pressure": {
                "repair_pressure": 0.4,
                "capacity_pressure": 0.5
            }
        },
        "durability_pressure_observed": True,
        "session_active": True
    }

def test_derive_pressure_summary(mock_session_state):
    """Validates pressure summary derivation."""
    summary = domain_dashboard_snapshot_builder.derive_pressure_summary(mock_session_state)
    
    assert summary["combat_pressure"] == 0.5 # observed=True
    assert summary["capacity_pressure"] == 0.5 # 20/40
    assert summary["mutation_pressure"] == 0.4 # 2 mutations * 0.2
    assert summary["repair_burden"] == 0.4
    assert 0.0 <= summary["traversal_pressure"] <= 1.0
    assert 0.0 <= summary["escape_risk"] <= 1.0

def test_derive_equipment_summary(mock_session_state):
    """Validates equipment summary derivation."""
    summary = domain_dashboard_snapshot_builder.derive_equipment_summary(mock_session_state)
    
    assert summary["damaged_items"] == 1
    assert summary["zero_durability_items"] == 0
    assert summary["repair_materials_remaining"] == 3

def test_derive_resource_summary(mock_session_state):
    """Validates resource summary derivation."""
    summary = domain_dashboard_snapshot_builder.derive_resource_summary(mock_session_state)
    
    assert summary["gold"] == 1250.0
    assert summary["potions"] == 5

def test_build_domain_dashboard_snapshot_schema_compatible(mock_session_state):
    """Validates that created snapshots match the schema."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state)
    assert res["ok"] is True
    snapshot = res["snapshot"]
    
    validation = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert validation["ok"] is True
    
    assert snapshot["player_id"] == "test_player_1"
    assert snapshot["floor_id"] == 2
    assert snapshot["run_status"] == "ACTIVE"

def test_summarize_dashboard_snapshot(mock_session_state):
    """Validates human-readable summary."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state)
    summary = domain_dashboard_snapshot_builder.summarize_dashboard_snapshot(res["snapshot"])
    
    assert "Floor 2" in summary
    assert "Combat:0.50" in summary
    assert "Gold:1250.0" in summary

def test_debug_safety(mock_session_state):
    """Validates that debug=True doesn't break logic."""
    domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state, debug=True)
