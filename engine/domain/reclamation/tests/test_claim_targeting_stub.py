import pytest
import os
import json
from engine.domain.reclamation import claim_targeting_stub

@pytest.fixture
def mock_claim():
    return {
        "claim_id": "c1",
        "visibility_pressure": 0.5
    }

def test_calculate_claim_targeting_stable(mock_claim):
    """Validates targeting for a stable claim."""
    res = claim_targeting_stub.calculate_claim_targeting(mock_claim, floor_reclamation_pressure=0.0)
    
    # visibility 0.5 * 0.7 = 0.35
    # scar 0
    # mult 1.0
    # total 0.35
    assert res["targeting_pressure"] == 0.35
    assert res["maintenance_penalty"] == 0
    assert res["is_destabilized"] is False

def test_calculate_claim_targeting_irritated(mock_claim):
    """Validates targeting scaling with reclamation pressure."""
    res = claim_targeting_stub.calculate_claim_targeting(mock_claim, floor_reclamation_pressure=0.8)
    
    # (0.35) * (1.0 + 0.4) = 0.49
    assert res["targeting_pressure"] == 0.49

def test_calculate_claim_targeting_scarred(mock_claim):
    """Validates targeting scaling with local scarring."""
    res = claim_targeting_stub.calculate_claim_targeting(mock_claim, floor_reclamation_pressure=0.0, local_scarring=1.0)
    
    # (0.35 + 0.3) * 1.0 = 0.65
    assert res["targeting_pressure"] == 0.65
    assert res["maintenance_penalty"] == 1

def test_calculate_claim_targeting_critical(mock_claim):
    """Validates targeting thresholds for penalty and destabilization."""
    # high visibility + high reclamation
    mock_claim["visibility_pressure"] = 1.0
    res = claim_targeting_stub.calculate_claim_targeting(mock_claim, floor_reclamation_pressure=1.0)
    
    # (0.7 + 0) * 1.5 = 1.0 (clamped)
    assert res["targeting_pressure"] == 1.0
    assert res["maintenance_penalty"] == 2
    assert res["is_destabilized"] is True

def test_summarize_targeting(mock_claim):
    """Validates human-readable summary."""
    res = claim_targeting_stub.calculate_claim_targeting(mock_claim, 0.0)
    summary = claim_targeting_stub.summarize_targeting(res)
    assert "0.35" in summary
    assert "STABLE" in summary
