import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_cap_dir"

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

def test_transcript_captures_capacity_pressure_success():
    """
    Validates that the transcript reporter captures capacity pressure evidence
    from status and combat commands.
    """
    commands = ["status", "combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="capacity_pressure_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["capacity_pressure_observed"] is True
    assert len(transcript["capacity_pressure_values_observed"]) >= 2
    assert "EMPTY" in transcript["capacity_bands_observed"]
    assert transcript["highest_capacity_pressure_observed"] >= 0.0
    assert len(transcript["material_burden_summaries"]) >= 2

def test_transcript_captures_over_capacity_failure():
    """
    Validates that the transcript can record over-capacity failures.
    We'll verify the fields exist and are initialized.
    """
    commands = ["status"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert "over_capacity_failures_observed" in transcript
    assert transcript["over_capacity_failures_observed"] == 0

def test_transcript_preserves_material_drain_evidence():
    """Validates that material drain evidence (repair/potion) is still captured."""
    commands = ["potion 1", "repair 1"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["inventory_transactions_observed"] == 2
    assert transcript["failed_consumable_attempts_observed"] == 1
    assert transcript["failed_repair_attempts_observed"] == 1
