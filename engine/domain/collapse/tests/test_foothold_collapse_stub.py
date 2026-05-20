import pytest

from engine.domain.collapse import foothold_collapse_stub


@pytest.fixture
def mock_claim():
    return {
        "claim_id": "claim_test_2",
        "status": "ACTIVE",
        "recovery_value": 0.2,
        "territorial_instability": 0.9
    }


def test_collapse_is_partial_and_bounded(mock_claim):
    record = foothold_collapse_stub.evaluate_foothold_collapse(mock_claim)
    assert 0.0 <= record["collapse_level"] <= 1.0
    assert record["collapse_level"] > 0.0
    assert record["collapse_band"] in ["MINOR", "PARTIAL", "SEVERE"]
    assert record["bounded_flags_clean"] is True
    assert record["claim_id"] == "claim_test_2"


def test_effective_recovery_degrades_but_not_deleted(mock_claim):
    record = foothold_collapse_stub.evaluate_foothold_collapse(mock_claim)
    assert record["effective_recovery_value"] <= mock_claim["recovery_value"]
    assert record["effective_recovery_value"] >= 0.0

