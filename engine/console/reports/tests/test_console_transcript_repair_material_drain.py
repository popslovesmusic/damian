import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_repair_dir"

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

def test_transcript_captures_repair_material_drain_failure():
    """
    Validates that the transcript reporter captures failed repair material attempts.
    """
    commands = ["repair 1"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=_get_test_paths(), debug=True, transcript_id="repair_material_drain_validation"
    )
    
    # ok is False because the command failed (no materials in inventory)
    assert transcript["ok"] is False
    assert transcript["inventory_transactions_observed"] == 1
    assert transcript["failed_repair_attempts_observed"] == 1
    assert transcript["repair_material_uses_observed"] == 0
    assert transcript["durability_restoration_observed"] is False
    assert len(transcript["repair_drain_summaries"]) == 1

def test_transcript_preserves_consumable_evidence():
    """Validates that consumable drain evidence is still captured."""
    commands = ["potion 1"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["failed_consumable_attempts_observed"] == 1
    assert "consumable_uses_observed" in transcript

def test_transcript_preserves_inventory_evidence():
    """Validates that inventory transactions are still captured."""
    commands = ["combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["inventory_transactions_observed"] >= 1
    assert transcript["total_gold_added_to_inventory"] >= 10000
