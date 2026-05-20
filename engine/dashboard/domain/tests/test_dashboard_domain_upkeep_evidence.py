import pytest
import os
import json
from engine.dashboard.domain import domain_dashboard_snapshot_builder

@pytest.fixture
def mock_session_state_with_decaying_claims():
    return {
        "runtime_context": {
            "tower_state": {"current_floor": 2, "floor_memory": []},
            "player_progression": {"player_id": "test_player_1"}
        },
        "inventory_state": {"gold": 1000.0, "items": []},
        "equipment_loadout": {"equipped_items": []},
        "domain_claims": [
            {
                "claim_id": "c1",
                "status": "ACTIVE",
                "maintenance_pressure": 0.1,
                "visibility_pressure": 0.1,
                "mutation_threat": 0.1,
                "recovery_value": 0.2,
                "tower_hostility_preserved": True
            },
            {
                "claim_id": "c2",
                "status": "DECAYING",
                "maintenance_pressure": 0.3,
                "visibility_pressure": 0.5,
                "mutation_threat": 0.4,
                "recovery_value": 0.1,
                "tower_hostility_preserved": True
            }
        ],
        "session_active": True
    }

def test_derive_domain_claim_summary_with_decay(mock_session_state_with_decaying_claims):
    """Validates claim summary with decaying state."""
    summary = domain_dashboard_snapshot_builder.derive_domain_claim_summary(mock_session_state_with_decaying_claims)
    
    assert summary["active_claims"] == 1
    assert summary["decaying_claims"] == 1
    assert summary["highest_maintenance_pressure"] == 0.3
    assert summary["highest_visibility_pressure"] == 0.5

def test_summarize_snapshot_with_decay(mock_session_state_with_decaying_claims):
    """Validates human-readable summary includes decaying counts."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_decaying_claims)
    summary = domain_dashboard_snapshot_builder.summarize_dashboard_snapshot(res["snapshot"])
    
    assert "Claims (1 active, 1 decaying)" in summary

def test_snapshot_validates_with_decay_evidence(mock_session_state_with_decaying_claims):
    """Validates that snapshots with decay evidence match the schema."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_decaying_claims)
    validation = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(res["snapshot"])
    assert validation["ok"] is True
