import pytest
import os
import json
from engine.residue.mutation import mutation_scarring_stub

@pytest.fixture
def mock_claims():
    return [
        {
            "claim_id": "c1",
            "claim_node_id": "node_a",
            "visibility_pressure": 0.4,
            "status": "ACTIVE"
        },
        {
            "claim_id": "c2",
            "claim_node_id": "node_b",
            "visibility_pressure": 0.2,
            "status": "DECAYING"
        }
    ]

def test_calculate_localized_scarring_active(mock_claims):
    """Validates scarring calculation for an active claim."""
    res = mutation_scarring_stub.calculate_localized_scarring("node_a", mock_claims, 1)
    
    # baseline 0.1 + (visibility 0.4 * 0.5) + decay 0 + depth 0 = 0.3
    assert res["scar_intensity"] == 0.3
    assert res["hazard_bias"] == round(0.3 * 0.6, 4)

def test_calculate_localized_scarring_decaying(mock_claims):
    """Validates scarring calculation for a decaying claim."""
    res = mutation_scarring_stub.calculate_localized_scarring("node_b", mock_claims, 1)
    
    # baseline 0.1 + (visibility 0.2 * 0.5) + decay 0.2 + depth 0 = 0.4
    assert res["scar_intensity"] == 0.4

def test_calculate_localized_scarring_empty(mock_claims):
    """Validates scarring calculation for a node without a claim."""
    res = mutation_scarring_stub.calculate_localized_scarring("node_c", mock_claims, 1)
    
    # baseline 0.1 + 0 + 0 + 0 = 0.1
    assert res["scar_intensity"] == 0.1

def test_calculate_localized_scarring_depth(mock_claims):
    """Validates scarring scaling with floor depth."""
    res1 = mutation_scarring_stub.calculate_localized_scarring("node_a", mock_claims, 1)
    res2 = mutation_scarring_stub.calculate_localized_scarring("node_a", mock_claims, 7)
    
    assert res2["scar_intensity"] > res1["scar_intensity"]

def test_summarize_scarring(mock_claims):
    """Validates human-readable summary."""
    res = mutation_scarring_stub.calculate_localized_scarring("node_a", mock_claims, 1)
    summary = mutation_scarring_stub.summarize_scarring(res)
    assert "node_a" in summary
    assert "0.30" in summary
