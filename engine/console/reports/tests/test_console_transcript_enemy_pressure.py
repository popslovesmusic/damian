import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_pressure_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_transcript_captures_enemy_pressure_evidence():
    """
    Validates that the transcript reporter captures enemy archetype,
    pressure profiles, and reasoning from combat commands.
    """
    commands = ["combat safe", "combat dangerous", "combat exhausted"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True, transcript_id="enemy_pressure_test"
    )
    
    assert transcript["ok"] is True
    assert transcript["combat_sessions_observed"] == 3
    assert transcript["enemy_pressure_profiles_observed"] == 3
    assert len(transcript["enemy_archetypes_observed"]) >= 1
    assert len(transcript["enemy_adaptation_reasoning_observed"]) >= 1
    
    # Check if at least one category flag is true
    categories = [
        "attrition_pressure_observed",
        "counter_pressure_observed",
        "ambush_pressure_observed",
        "baseline_pressure_observed"
    ]
    assert any(transcript[cat] for cat in categories)

def test_transcript_preserves_combat_observations():
    """Validates that existing combat observations are still captured."""
    commands = ["combat safe", "combat dangerous"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["combat_sessions_observed"] == 2
    assert len(transcript["combat_outcomes_observed"]) == 2
    assert transcript["resource_pressure_observed"] in [True, False]
    assert transcript["residue_pressure_observed"] in [True, False]

def test_transcript_captures_reasoning_uniqueness():
    """Validates that reasoning strings are aggregated uniquely."""
    commands = ["combat safe", "combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    # Reasoning should be captured, and should be unique in the list
    reasoning = transcript["enemy_adaptation_reasoning_observed"]
    assert len(reasoning) == len(set(reasoning))
