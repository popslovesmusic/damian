import pytest
import os
import json
from engine.domain.reclamation import tower_reclamation_pressure_stub

@pytest.fixture
def mock_claims():
    return [
        {
            "claim_id": "c1",
            "visibility_pressure": 0.2,
            "status": "ACTIVE"
        },
        {
            "claim_id": "c2",
            "visibility_pressure": 0.4,
            "status": "DECAYING"
        }
    ]

def test_calculate_reclamation_pressure_scaling(mock_claims):
    """Validates reclamation pressure scaling with visibility and decay."""
    # Floor 1
    res1 = tower_reclamation_pressure_stub.calculate_reclamation_pressure(1, mock_claims)
    
    # visibility = (0.2 + 0.4) * 0.5 = 0.3
    # decay = 1 * 0.2 = 0.2
    # depth = 1 // 3 * 0.1 = 0.0
    # total = 0.5
    assert res1["total_reclamation_pressure"] == 0.5
    assert res1["reclamation_band"] == "HOSTILE"
    
    # Floor 5 (Depth increases)
    res2 = tower_reclamation_pressure_stub.calculate_reclamation_pressure(5, mock_claims)
    # depth = 5 // 3 * 0.1 = 0.1
    # total = 0.6
    assert res2["total_reclamation_pressure"] == 0.6

def test_get_reclamation_band():
    """Validates pressure to band mapping."""
    assert tower_reclamation_pressure_stub.get_reclamation_band(0.1) == "STABLE"
    assert tower_reclamation_pressure_stub.get_reclamation_band(0.5) == "HOSTILE"
    assert tower_reclamation_pressure_stub.get_reclamation_band(0.9) == "CRITICAL"

def test_validate_reclamation_pressure(mock_claims):
    """Validates that reclamation records match the schema."""
    res = tower_reclamation_pressure_stub.calculate_reclamation_pressure(1, mock_claims)
    validation = tower_reclamation_pressure_stub.validate_reclamation_pressure(res)
    assert validation["ok"] is True

def test_summarize_reclamation_pressure(mock_claims):
    """Validates human-readable summary."""
    res = tower_reclamation_pressure_stub.calculate_reclamation_pressure(1, mock_claims)
    summary = tower_reclamation_pressure_stub.summarize_reclamation_pressure(res)
    assert "HOSTILE" in summary
    assert "0.50" in summary
