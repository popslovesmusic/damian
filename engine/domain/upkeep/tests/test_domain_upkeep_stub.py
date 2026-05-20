import pytest
import os
import json
from engine.domain.upkeep import domain_upkeep_stub

@pytest.fixture
def mock_claim():
    return {
        "claim_id": "c1",
        "floor_id": 1,
        "claim_type": "recovery_anchor",
        "status": "ACTIVE"
    }

def test_calculate_upkeep_cost(mock_claim):
    """Validates upkeep cost calculation scaling with floor and type."""
    # Floor 1, recovery_anchor
    cost1 = domain_upkeep_stub.calculate_upkeep_cost(mock_claim)
    assert cost1 == 1 # (1 + 0) * 1.0
    
    # Floor 5, survivor_outpost
    mock_claim["floor_id"] = 5
    mock_claim["claim_type"] = "survivor_outpost"
    cost2 = domain_upkeep_stub.calculate_upkeep_cost(mock_claim)
    # (1 + 5//3) * 2.0 = (1 + 1) * 2.0 = 4
    assert cost2 == 4

def test_calculate_upkeep_cost_with_penalty(mock_claim):
    """Validates that maintenance penalty increases cost."""
    base_cost = domain_upkeep_stub.calculate_upkeep_cost(mock_claim)
    penalty_cost = domain_upkeep_stub.calculate_upkeep_cost(mock_claim, maintenance_penalty=2)
    assert penalty_cost == base_cost + 2

def test_process_claim_upkeep_success(mock_claim):
    """Validates successful upkeep payment."""
    res = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=10)
    assert res["ok"] is True
    assert res["upkeep_event"]["upkeep_successful"] is True
    assert res["updated_status"] == "ACTIVE"
    assert res["shards_consumed"] == 1

def test_process_claim_upkeep_decay(mock_claim):
    """Validates state decay on non-payment."""
    # ACTIVE -> DECAYING
    res1 = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=0)
    assert res1["updated_status"] == "DECAYING"
    assert res1["upkeep_event"]["upkeep_successful"] is False
    
    # DECAYING -> OVERRUN
    mock_claim["status"] = "DECAYING"
    res2 = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=0)
    assert res2["updated_status"] == "OVERRUN"
    
    # OVERRUN -> OVERRUN
    mock_claim["status"] = "OVERRUN"
    res3 = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=0)
    assert res3["updated_status"] == "OVERRUN"

def test_process_claim_upkeep_restoration(mock_claim):
    """Validates state restoration on payment."""
    mock_claim["status"] = "DECAYING"
    res = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=10)
    assert res["updated_status"] == "ACTIVE"
    assert res["upkeep_event"]["upkeep_successful"] is True

def test_validate_upkeep_event(mock_claim):
    """Validates that upkeep events match the schema."""
    res = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=1)
    validation = domain_upkeep_stub.validate_upkeep_event(res["upkeep_event"])
    assert validation["ok"] is True

def test_summarize_upkeep_event(mock_claim):
    """Validates human-readable summary."""
    res = domain_upkeep_stub.process_claim_upkeep(mock_claim, available_shards=1)
    summary = domain_upkeep_stub.summarize_upkeep_event(res["upkeep_event"])
    assert "Paid" in summary
    assert "ACTIVE -> ACTIVE" in summary
