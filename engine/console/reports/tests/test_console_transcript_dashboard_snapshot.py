import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_dashboard_snapshot_dir"

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

def test_transcript_captures_dashboard_snapshot_success():
    """
    Validates that the transcript reporter captures dashboard snapshots
    and survival summaries.
    """
    commands = ["status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="dashboard_snapshot_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["dashboard_snapshots_observed"] >= 1
    assert transcript["dashboard_status_observed"] is True
    assert len(transcript["pressure_summaries_observed"]) >= 1
    assert len(transcript["resource_summaries_observed"]) >= 1
    assert len(transcript["equipment_summaries_observed"]) >= 1
    assert len(transcript["route_summaries_observed"]) >= 1
    assert len(transcript["residue_summaries_observed"]) >= 1
    assert len(transcript["recoverability_statuses_observed"]) >= 1
    assert len(transcript["dashboard_survival_summaries"]) >= 1
    
    # Check content of a summary
    snapshot = transcript["pressure_summaries_observed"][0]
    assert "combat_pressure" in snapshot
    assert "capacity_pressure" in snapshot

def test_transcript_preserves_traversal_and_escape_evidence():
    """Validates that dashboard capture doesn't break other spatial observations."""
    commands = ["status", "advance", "escape"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["dashboard_snapshots_observed"] >= 1
    assert transcript["traversal_events_observed"] >= 2
    assert transcript["escape_resolutions_observed"] >= 1

def test_transcript_dashboard_longitudinal_tracking():
    """Validates aggregation of multiple snapshots in a single session."""
    commands = ["status", "combat safe", "status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True
    )
    
    assert transcript["dashboard_snapshots_observed"] == 2
    assert len(transcript["pressure_summaries_observed"]) == 2
    assert len(transcript["dashboard_survival_summaries"]) == 2
