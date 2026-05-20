import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_escape_resolution_dir"

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

def test_transcript_captures_escape_resolution_success():
    """
    Validates that the transcript reporter captures escape outcomes,
    successes, and residue.
    """
    # Low risk escape
    commands = ["escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="escape_resolution_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["escape_resolutions_observed"] >= 1
    assert transcript["escape_successes_observed"] >= 1
    assert transcript["escape_residue_written_observed"] is True
    assert "ESCAPE_SUCCESS" in transcript["escape_resolution_summaries"][0]
    assert "RETREAT_TO_HUB" in transcript["escape_pipeline_outcomes_observed"]

def test_transcript_captures_severe_escape_failure(monkeypatch):
    """Validates capture of severe retreat drop consequences."""
    # Force severe failure via mocking
    from engine.traversal.escape import escape_resolution_stub
    original_resolve = escape_resolution_stub.resolve_escape_attempt
    def mock_resolve(*args, **kwargs):
        res = original_resolve(*args, **kwargs)
        if res["ok"]:
            res["escape_resolution"]["outcome"] = "ESCAPE_FAILED_RETREAT_DROP"
            res["escape_resolution"]["pipeline_outcome"] = "DEFEAT_DROP"
            res["escape_resolution"]["mutation_pressure_delta"] = 0.2
            res["escape_resolution"]["resource_loss"]["gold"] = 1000
        return res
    monkeypatch.setattr(escape_resolution_stub, "resolve_escape_attempt", mock_resolve)

    commands = ["escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    # ok might be True or False depending on pipeline, but resolution should be observed
    assert transcript["escape_resolutions_observed"] == 1
    assert transcript["escape_failures_observed"] == 1
    assert transcript["severe_escape_failures_observed"] == 1
    assert transcript["escape_mutation_pressure_observed"] is True
    assert transcript["total_escape_mutation_pressure_delta"] == 0.2
    assert len(transcript["escape_resource_losses_observed"]) == 1
    assert transcript["escape_resource_losses_observed"][0]["gold"] == 1000
    assert "DEFEAT_DROP" in transcript["escape_pipeline_outcomes_observed"]

def test_transcript_preserves_safety_flags():
    """Validates that recoverability is tracked in transcripts."""
    commands = ["escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["escape_recoverability_preserved"] is True
    assert transcript["escape_floor_identity_preserved"] is True

def test_transcript_preserves_traversal_evidence():
    """Validates that escape resolution doesn't break basic traversal checks."""
    commands = ["escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["traversal_events_observed"] >= 1
    assert transcript["escape_attempts_observed"] >= 1
