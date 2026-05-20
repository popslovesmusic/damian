import pytest
import os
import json
from engine.dashboard.domain import domain_dashboard_snapshot_builder

@pytest.fixture
def mock_session_state_with_scarring():
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
                "claim_node_id": "node_a",
                "status": "ACTIVE",
                "visibility_pressure": 0.5
            },
            {
                "claim_id": "c2",
                "claim_node_id": "node_b",
                "status": "DECAYING",
                "visibility_pressure": 0.2
            }
        ],
        "session_active": True
    }

def test_derive_mutation_scarring_summary(mock_session_state_with_scarring):
    """Validates mutation scarring summary derivation."""
    summary = domain_dashboard_snapshot_builder.derive_mutation_scarring_summary(mock_session_state_with_scarring)
    
    assert summary["scarred_nodes_count"] == 2
    # Node A intensity = 0.1 + (0.5 * 0.5) + 0 + 0 = 0.35
    # Node B intensity = 0.1 + (0.2 * 0.5) + 0.2 + 0 = 0.4
    assert summary["highest_scar_intensity"] == 0.4
    assert summary["aggregate_hazard_bias"] > 0

def test_snapshot_includes_scarring_evidence(mock_session_state_with_scarring):
    """Validates that snapshots include scarring records."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_scarring)
    assert res["ok"] is True
    snapshot = res["snapshot"]
    
    assert "mutation_scarring_summary" in snapshot
    assert snapshot["mutation_scarring_summary"]["highest_scar_intensity"] == 0.4
    
    # Schema validation
    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True

def test_summarize_snapshot_with_scarring(mock_session_state_with_scarring):
    """Validates human-readable summary includes scarring intensity."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_scarring)
    summary = domain_dashboard_snapshot_builder.summarize_dashboard_snapshot(res["snapshot"])
    
    assert "Scarring: 0.40 (2 nodes)" in summary
