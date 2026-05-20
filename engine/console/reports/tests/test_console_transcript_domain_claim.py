import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_domain_claim_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def _get_test_paths():
    paths = mvp_startup_orchestrator.make_default_runtime_paths()
    paths["tower_state"] = os.path.join(TEST_DIR, "tower_state.json")
    paths["player_progression"] = os.path.join(TEST_DIR, "player_progression.json")
    paths["domain_state"] = os.path.join(TEST_DIR, "domain_state.json")
    return paths

def test_transcript_captures_domain_claim_success():
    """
    Validates that the transcript reporter captures domain claim evidence.
    """
    commands = ["claim", "claim repair_station"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="domain_claim_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["domain_claims_observed"] == 2
    assert "recovery_anchor" in transcript["domain_claim_types_observed"]
    assert "repair_station" in transcript["domain_claim_types_observed"]
    
    assert 0.0 <= transcript["highest_domain_maintenance_pressure_observed"] <= 1.0
    assert 0.0 <= transcript["highest_domain_visibility_pressure_observed"] <= 1.0
    assert 0.0 <= transcript["highest_domain_mutation_threat_observed"] <= 1.0
    assert transcript["total_domain_recovery_value_observed"] > 0
    assert transcript["tower_hostility_preserved_observed"] is True
    assert len(transcript["domain_claim_summaries"]) == 2

def test_transcript_preserves_dashboard_evidence():
    """Validates that domain claim capture doesn't break dashboard observations."""
    commands = ["claim", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["domain_claims_observed"] >= 1
    assert transcript["dashboard_snapshots_observed"] >= 1

def test_transcript_domain_claim_longitudinal_tracking():
    """Validates aggregation of claim pressures in a single session."""
    # We use a deeper floor to get higher maintenance pressure
    # But for a simple test we just verify it tracks multiple claims
    commands = ["claim recovery_anchor", "claim survivor_outpost"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["domain_claims_observed"] == 2
    assert len(transcript["domain_claim_summaries"]) == 2
    
    # Survivor outpost typically has higher visibility
    assert transcript["highest_domain_visibility_pressure_observed"] > 0
