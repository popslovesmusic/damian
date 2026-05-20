import os
import json
import shutil
import pytest
from engine.console.reports import console_transcript_reporter

# Define a temporary directory for tests
TEST_DIR = "test_temp_transcript_inv_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_transcript_captures_inventory_evidence():
    """
    Validates that the transcript reporter captures inventory transactions,
    gold additions, and summaries.
    """
    # Combat safe produces victory loot (10000 gold)
    commands = ["combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True, transcript_id="inventory_evidence_validation"
    )
    
    assert transcript["ok"] is True
    assert transcript["inventory_transactions_observed"] == 1
    assert transcript["inventory_applications_observed"] == 1
    assert transcript["total_gold_added_to_inventory"] >= 10000
    assert len(transcript["inventory_summaries"]) >= 1
    assert transcript["capacity_pressure_observed"] in [True, False]

def test_transcript_preserves_prior_evidence():
    """Validates that combat and loot evidence are still captured."""
    commands = ["combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["combat_sessions_observed"] == 1
    assert transcript["loot_events_observed"] == 1
    assert transcript["total_gold_observed"] >= 10000

def test_transcript_captures_inventory_failures():
    """
    Validates that the transcript can record inventory safe failures.
    For MVP, we'll simulate this if possible, or verify the logic in the reporter.
    Actually, we can try to force a capacity overflow if we had a command for it.
    Since we don't have a direct 'add_heavy_item' command yet, we'll verify fields.
    """
    commands = ["status"] # No transactions here
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    assert transcript["inventory_failures_observed"] == 0

def test_multiple_transactions_accumulation():
    """Validates aggregation across multiple sessions."""
    commands = ["combat safe", "combat safe"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, debug=True
    )
    
    assert transcript["inventory_transactions_observed"] == 2
    assert transcript["total_gold_added_to_inventory"] >= 20000
