import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_loot_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_transcript_captures_loot_evidence():
    """
    Validates that the transcript reporter captures loot events,
    gold amounts, and resource sink pressure.
    """
    # Victory combat script to ensure 10000 gold
    commands = ["combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True, transcript_id="loot_evidence_test"
    )
    
    assert transcript["ok"] is True
    assert transcript["loot_events_observed"] == 1
    assert transcript["total_gold_observed"] >= 10000
    assert transcript["large_visible_loot_observed"] is True
    assert transcript["resource_sink_pressure_observed"] is True
    assert transcript["bounded_reward_flags_clean"] is True
    assert len(transcript["resource_sink_summaries"]) >= 1
    assert "combat_reward" in transcript["loot_sources_observed"]

def test_transcript_preserves_prior_evidence():
    """Validates that enemy pressure and combat evidence are still captured."""
    commands = ["combat dangerous"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["combat_sessions_observed"] == 1
    assert transcript["enemy_pressure_profiles_observed"] == 1
    assert len(transcript["enemy_archetypes_observed"]) >= 1

def test_transcript_handles_multiple_loot_events():
    """Validates aggregation across multiple combat sessions."""
    commands = ["combat safe", "combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["loot_events_observed"] == 2
    assert transcript["total_gold_observed"] >= 20000
    # Summaries might be duplicated if on same floor, but should be captured
    assert len(transcript["resource_sink_summaries"]) >= 1
