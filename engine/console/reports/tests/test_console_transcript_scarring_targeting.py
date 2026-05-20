import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_scarring_targeting_dir"

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

def test_transcript_captures_scarring_and_targeting_success():
    """
    Validates that the transcript reporter captures mutation scarring
    and claim targeting evidence.
    """
    commands = ["claim survivor_outpost", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="scarring_targeting_validation"
    )
    
    assert transcript["ok"] is True
    
    # Check Scarring (from status)
    assert transcript["scarred_nodes_observed"] >= 1
    assert transcript["highest_scar_intensity_observed"] > 0
    assert len(transcript["scarring_summaries"]) >= 1
    
    # Check Targeting (from claim)
    assert transcript["highest_targeting_pressure_observed"] > 0
    assert len(transcript["targeting_summaries"]) >= 1
    assert transcript["tower_hostility_preserved_observed"] is True

def test_transcript_preserves_reclamation_evidence():
    """Validates that scarring capture doesn't break reclamation observations."""
    commands = ["claim", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["reclamation_pressure_observed"] is True
    assert transcript["scarred_nodes_observed"] >= 1
