import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_room_route_evidence_dir"

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

def test_transcript_captures_room_route_evidence_success():
    """
    Validates that the transcript reporter captures room graphs,
    selected routes, environmental profiles, and route exposure.
    """
    commands = ["advance", "escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="room_route_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["room_graph_evidence_observed"] is True
    assert transcript["room_route_evidence_observed"] is True
    assert transcript["room_routes_observed"] >= 1
    assert len(transcript["selected_routes_observed"]) >= 2
    assert len(transcript["route_types_observed"]) >= 2
    assert len(transcript["environmental_profiles_observed"]) >= 2
    assert len(transcript["route_exposure_values_observed"]) >= 2
    assert len(transcript["escape_modifiers_observed"]) >= 1 # After escape command
    assert transcript["route_pressure_used_observed"] is True
    assert len(transcript["room_route_summaries"]) >= 2

def test_transcript_captures_highest_route_exposure():
    """Validates tracking of peak route exposure."""
    commands = ["advance", "advance"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    vals = transcript["route_exposure_values_observed"]
    if vals:
        assert transcript["highest_route_exposure_observed"] == max(vals)

def test_transcript_preserves_traversal_pressure_evidence():
    """Validates that room route capture doesn't break traversal pressure observations."""
    commands = ["advance"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["traversal_events_observed"] >= 1
    assert transcript["advance_attempts_observed"] == 1
    assert transcript["traversal_pressure_observed"] is True
