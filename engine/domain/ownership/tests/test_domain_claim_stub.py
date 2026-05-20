import pytest
import os
import json
from engine.domain.ownership import domain_claim_stub

def test_make_domain_claim_recovery_anchor():
    """Validates creation of recovery_anchor claim."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_a", "recovery_anchor")
    assert res["ok"] is True
    claim = res["domain_claim"]
    assert claim["claim_type"] == "recovery_anchor"
    assert claim["maintenance_pressure"] == 0.10 # 0.10 bias + 0 floor factor
    assert claim["recoverability_supported"] is True
    assert claim["tower_hostility_preserved"] is True

def test_make_domain_claim_supply_cache():
    """Validates creation of supply_cache claim."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_b", "supply_cache")
    assert res["ok"] is True
    assert res["domain_claim"]["claim_type"] == "supply_cache"
    assert res["domain_claim"]["visibility_pressure"] == 0.18

def test_make_domain_claim_repair_station():
    """Validates creation of repair_station claim."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_c", "repair_station")
    assert res["ok"] is True
    assert res["domain_claim"]["claim_type"] == "repair_station"

def test_make_domain_claim_survivor_outpost():
    """Validates creation of survivor_outpost claim."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_d", "survivor_outpost")
    assert res["ok"] is True
    assert res["domain_claim"]["claim_type"] == "survivor_outpost"

def test_make_domain_claim_observation_post():
    """Validates creation of observation_post claim."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_e", "observation_post")
    assert res["ok"] is True
    assert res["domain_claim"]["claim_type"] == "observation_post"

def test_pressure_scaling_with_floor():
    """Validates that pressure increases with floor depth."""
    p1 = domain_claim_stub.calculate_domain_claim_pressure("recovery_anchor", 1)
    p2 = domain_claim_stub.calculate_domain_claim_pressure("recovery_anchor", 5)
    
    assert p2["maintenance_pressure"] > p1["maintenance_pressure"]
    assert p2["visibility_pressure"] > p1["visibility_pressure"]

def test_pressure_scaling_with_residue():
    """Validates that mutation threat increases with residue strength."""
    p1 = domain_claim_stub.calculate_domain_claim_pressure("recovery_anchor", 1, residue_strength=0.1)
    p2 = domain_claim_stub.calculate_domain_claim_pressure("recovery_anchor", 1, residue_strength=0.8)
    
    assert p2["mutation_threat"] > p1["mutation_threat"]

def test_make_domain_claim_schema_compatible():
    """Validates that created claims match the schema."""
    res = domain_claim_stub.make_domain_claim("p1", 2, "node_x", "recovery_anchor")
    assert res["ok"] is True
    validation = domain_claim_stub.validate_domain_claim(res["domain_claim"])
    assert validation["ok"] is True

def test_invalid_claim_type_fails_safely():
    """Validates safe failure for unknown claim types."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_a", "mansion")
    assert res["ok"] is False
    assert res["error"] == "InvalidClaimType"

def test_invalid_floor_id_fails_safely():
    """Validates safe failure for invalid floor IDs."""
    res = domain_claim_stub.make_domain_claim("p1", -5, "node_a", "recovery_anchor")
    assert res["ok"] is False
    assert res["error"] == "InvalidFloorID"

def test_summarize_domain_claim():
    """Validates human-readable summary."""
    res = domain_claim_stub.make_domain_claim("p1", 1, "node_a", "recovery_anchor")
    summary = domain_claim_stub.summarize_domain_claim(res["domain_claim"])
    assert "recovery_anchor" in summary
    assert "Floor 1" in summary

def test_debug_safety():
    """Validates that debug=True doesn't break logic."""
    domain_claim_stub.make_domain_claim("p1", 1, "node_a", debug=True)
