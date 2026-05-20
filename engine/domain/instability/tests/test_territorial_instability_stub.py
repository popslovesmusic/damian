import pytest

from engine.domain.instability import territorial_instability_stub


@pytest.fixture
def mock_claim():
    return {
        "claim_id": "claim_test_1",
        "status": "ACTIVE",
        "territorial_instability": 0.0
    }


def test_instability_increases_under_targeting_and_neglect(mock_claim):
    targeting = {"targeting_pressure": 0.85, "maintenance_penalty": 2, "is_destabilized": True}
    record = territorial_instability_stub.calculate_territorial_instability(
        mock_claim, targeting_record=targeting, upkeep_successful=False
    )
    assert record["instability"] > record["previous_instability"]
    assert 0.0 <= record["instability"] <= 1.0
    assert record["bounded_flags_clean"] is True


def test_instability_decreases_under_successful_upkeep(mock_claim):
    mock_claim["territorial_instability"] = 0.6
    targeting = {"targeting_pressure": 0.2, "maintenance_penalty": 0, "is_destabilized": False}
    record = territorial_instability_stub.calculate_territorial_instability(
        mock_claim, targeting_record=targeting, upkeep_successful=True
    )
    assert record["instability"] < record["previous_instability"]
    assert 0.0 <= record["instability"] <= 1.0

