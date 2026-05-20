import pytest
import os
import json
import datetime
from engine.dashboard.domain import domain_dashboard_snapshot_builder

@pytest.fixture
def mock_session_state_with_claims():
    return {
        "runtime_context": {
            "tower_state": {
                "current_floor": 2,
                "floor_memory": []
            },
            "player_progression": {
                "player_id": "test_player_1",
                "highest_floor_reached": 3
            }
        },
        "inventory_state": {
            "gold": 1250.0,
            "items": []
        },
        "equipment_loadout": {
            "equipped_items": []
        },
        "domain_claims": [
            {
                "claim_id": "c1",
                "claim_type": "recovery_anchor",
                "status": "ACTIVE",
                "maintenance_pressure": 0.1,
                "visibility_pressure": 0.15,
                "mutation_threat": 0.05,
                "recovery_value": 0.25,
                "tower_hostility_preserved": True
            },
            {
                "claim_id": "c2",
                "claim_type": "supply_cache",
                "status": "DECAYING",
                "maintenance_pressure": 0.3,
                "visibility_pressure": 0.45,
                "mutation_threat": 0.2,
                "recovery_value": 0.1,
                "tower_hostility_preserved": True
            }
        ],
        "session_active": True
    }

def test_derive_domain_claim_summary(mock_session_state_with_claims):
    """Validates domain claim summary derivation."""
    summary = domain_dashboard_snapshot_builder.derive_domain_claim_summary(mock_session_state_with_claims)
    
    assert summary["active_claims"] == 1
    assert summary["decaying_claims"] == 1
    assert summary["overrun_claims"] == 0
    assert summary["highest_maintenance_pressure"] == 0.3
    assert summary["highest_visibility_pressure"] == 0.45
    assert summary["highest_mutation_threat"] == 0.2
    assert summary["total_recovery_value"] == 0.35
    assert summary["tower_hostility_preserved"] is True

def test_build_snapshot_with_claim_evidence(mock_session_state_with_claims):
    """Validates that snapshots include claim evidence and pass validation."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_claims)
    assert res["ok"] is True
    snapshot = res["snapshot"]
    
    assert "domain_claim_summary" in snapshot
    assert snapshot["domain_claim_summary"]["active_claims"] == 1
    
    # Schema validation
    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True

def test_summarize_snapshot_with_claims(mock_session_state_with_claims):
    """Validates human-readable summary includes claim counts."""
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_claims)
    summary = domain_dashboard_snapshot_builder.summarize_dashboard_snapshot(res["snapshot"])
    
    assert "Claims (1 active, 1 decaying)" in summary

def test_empty_claims_handled_safely():
    """Validates behavior when no claims exist."""
    session_state = {"domain_claims": []}
    summary = domain_dashboard_snapshot_builder.derive_domain_claim_summary(session_state)
    
    assert summary["active_claims"] == 0
    assert summary["highest_maintenance_pressure"] == 0.0
    assert summary["total_recovery_value"] == 0.0
    assert summary["tower_hostility_preserved"] is True
