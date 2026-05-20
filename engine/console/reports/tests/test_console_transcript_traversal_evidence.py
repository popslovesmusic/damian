import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_traversal_evidence_dir"

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

def test_transcript_captures_traversal_evidence_success():
    """
    Validates that the transcript reporter captures advance and escape attempts,
    traversal pressure, and risk.
    """
    commands = ["advance", "escape", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="traversal_evidence_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["traversal_events_observed"] >= 2
    assert transcript["advance_attempts_observed"] == 1
    assert transcript["escape_attempts_observed"] == 1
    assert transcript["traversal_pressure_observed"] is True
    assert transcript["escape_risk_observed"] is True
    assert len(transcript["traversal_pressure_values_observed"]) >= 3 # 2 commands + 1 status
    assert len(transcript["escape_risk_values_observed"]) >= 3
    assert len(transcript["traversal_summaries"]) >= 3
    assert transcript["highest_traversal_pressure_observed"] > 0
    assert transcript["highest_escape_risk_observed"] > 0

def test_transcript_preserves_other_evidence():
    """Validates that traversal capture doesn't break other observations."""
    commands = ["combat safe", "advance"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["combat_sessions_observed"] == 1
    assert transcript["traversal_events_observed"] == 1
    assert transcript["inventory_transactions_observed"] >= 1 # From combat loot

def test_highest_traversal_pressure_tracking():
    """Validates tracking of peak traversal pressure."""
    # We can't easily force high pressure without setting up inventory,
    # but we can verify it's at least the max of the observed values.
    commands = ["status", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    vals = transcript["traversal_pressure_values_observed"]
    if vals:
        assert transcript["highest_traversal_pressure_observed"] == max(vals)
