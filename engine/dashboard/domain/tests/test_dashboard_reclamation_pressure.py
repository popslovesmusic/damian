import pytest
import os
import json
from engine.dashboard.domain import domain_dashboard_snapshot_builder

@pytest.fixture
def mock_session_state_with_reclamation():
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
                "visibility_pressure": 0.4
            }
        ],
        "session_active": True
    }

def test_derive_reclamation_pressure(mock_session_state_with_reclamation):
    """Validates reclamation pressure derivation."""
    res = domain_dashboard_snapshot_builder.derive_reclamation_pressure(mock_session_state_with_reclamation)
    
    # Floor 2, 1 claim (vis 0.4)
    # vis contribution = 0.4 * 0.5 = 0.2
    # depth contribution = 2 // 3 * 0.1 = 0.0
    # total = 0.2
    assert res["total_reclamation_pressure"] == 0.2
    assert res["reclamation_band"] == "STABLE"

def test_snapshot_includes_reclamation_evidence(mock_session_state_with_reclamation):
    """Validates that snapshots include reclamation records."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_reclamation)
    assert res["ok"] is True
    snapshot = res["snapshot"]
    
    assert "reclamation_pressure" in snapshot
    assert snapshot["reclamation_pressure"]["total_reclamation_pressure"] == 0.2
    
    # Schema validation
    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True

def test_summarize_snapshot_with_reclamation(mock_session_state_with_reclamation):
    """Validates human-readable summary includes reclamation band."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_reclamation)
    summary = domain_dashboard_snapshot_builder.summarize_dashboard_snapshot(res["snapshot"])
    
    assert "Reclamation: STABLE (0.20)" in summary
