import pytest

from engine.dashboard.domain import domain_dashboard_snapshot_builder


@pytest.fixture
def mock_session_state_with_collapse():
    return {
        "runtime_context": {
            "tower_state": {"current_floor": 3, "floor_memory": []},
            "player_progression": {"player_id": "test_player_collapse"}
        },
        "inventory_state": {"gold": 0.0, "items": []},
        "equipment_loadout": {"equipped_items": []},
        "domain_claims": [
            {
                "claim_id": "c_collapse_1",
                "claim_node_id": "node_x",
                "status": "ACTIVE",
                "recovery_value": 0.2,
                "visibility_pressure": 0.4,
                "territorial_instability": 0.9
            }
        ],
        "session_active": True
    }


def test_snapshot_includes_foothold_collapse_evidence(mock_session_state_with_collapse):
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_collapse)
    assert res["ok"] is True
    snapshot = res["snapshot"]

    assert "foothold_collapse_summary" in snapshot
    col = snapshot["foothold_collapse_summary"]
    assert col["claims_evaluated"] == 1
    assert col["collapsed_footholds"] == 1
    assert col["highest_collapse_level"] > 0.0

    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True

