import pytest

from engine.dashboard.domain import domain_dashboard_snapshot_builder


@pytest.fixture
def mock_session_state_with_recovery():
    return {
        "runtime_context": {
            "tower_state": {"current_floor": 2, "floor_memory": []},
            "player_progression": {"player_id": "test_player_recovery"}
        },
        "inventory_state": {"gold": 0.0, "items": []},
        "equipment_loadout": {"equipped_items": []},
        "domain_claims": [],
        "foothold_recovery_history": [
            {
                "recovery_id": "rec_1",
                "claim_id": "c1",
                "effort": 1,
                "shards_spent": 5.0,
                "previous_instability": 0.8,
                "new_instability": 0.7,
                "previous_status": "OVERRUN",
                "new_status": "DECAYING",
                "bounded_flags_clean": True
            }
        ],
        "session_active": True
    }


def test_snapshot_includes_foothold_recovery_evidence(mock_session_state_with_recovery):
    res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(mock_session_state_with_recovery)
    assert res["ok"] is True
    snapshot = res["snapshot"]

    assert "foothold_recovery_summary" in snapshot
    rec = snapshot["foothold_recovery_summary"]
    assert rec["recovery_actions_taken"] == 1
    assert rec["total_shards_spent"] == 5.0
    assert rec["restored_from_overrun"] == 1

    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True

