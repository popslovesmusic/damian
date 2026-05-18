import pytest
import os
import json
import shutil
import sys
import datetime
import random
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.reports.runtime import replay_floor_diff_reporter
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper # To get a valid tower_state


# Paths to existing schemas
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FLOOR_MEMORY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_diff_reporter_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # Create dummy floor memory schema file for validation tests
    dummy_floor_memory_schema = {
        "type": "object",
        "properties": {
            "floor_id": {"type": "integer", "minimum": 1},
            "visit_count": {"type": "integer", "minimum": 0},
            "death_count": {"type": "integer", "minimum": 0},
            "victory_count": {"type": "integer", "minimum": 0},
            "stability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "deviation": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "mutation_level": {"type": "integer", "minimum": 0},
            "known_layout_seed": {"type": "string"},
            "active_mutations": {"type": "array", "items": {"type": "string"}},
            "discovered_easter_eggs": {"type": "array", "items": {"type": "string"}},
            "unclaimed_easter_eggs": {"type": "array", "items": {"type": "string"}},
            "residue_history": {"type": "array", "items": {"type": "object"}} # Simplified for this schema test
        },
        "required": ["floor_id", "visit_count", "death_count", "victory_count", "stability", "deviation", "mutation_level", "known_layout_seed", "active_mutations", "discovered_easter_eggs", "unclaimed_easter_eggs", "residue_history"]
    }
    os.makedirs(os.path.dirname(FLOOR_MEMORY_SCHEMA_PATH), exist_ok=True)
    with open(FLOOR_MEMORY_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_floor_memory_schema, f)

    yield
    shutil.rmtree(TEST_DIR)

# Mock debug_logger if it's not available for these tests
try:
    from engine.debug.runtime import debug_logger as real_debug_logger
except ImportError:
    class MockDebugLogger:
        def make_debug_event(self, *args, **kwargs):
            return {"mock_event": True}
        def write_debug_event(self, *args, **kwargs):
            return {"ok": True, "payload": "Mock log written"}
        def debug_enabled(self, *args, **kwargs):
            return True
    real_debug_logger = MockDebugLogger() # type: ignore

# Patch debug_logger for tests
@pytest.fixture
def mock_debug_logger():
    with patch('engine.reports.runtime.replay_floor_diff_reporter._debug_logger_available', True):
        with patch('engine.reports.runtime.replay_floor_diff_reporter.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Floor Memory ---
@pytest.fixture
def mock_floor_memory_before():
    return {
        "floor_id": 1,
        "visit_count": 1,
        "death_count": 0,
        "victory_count": 1,
        "stability": 0.8,
        "deviation": 0.1,
        "mutation_level": 0,
        "known_layout_seed": "seed_abc",
        "active_mutations": [],
        "discovered_easter_eggs": [],
        "unclaimed_easter_eggs": ["mark_initial"],
        "residue_history": [{"id": "res1"}]
    }

@pytest.fixture
def mock_floor_memory_after_mutation(mock_floor_memory_before):
    after = mock_floor_memory_before.copy()
    after["visit_count"] = 2
    after["death_count"] = 1
    after["mutation_level"] = 1
    after["stability"] = 0.75
    after["deviation"] = 0.15
    after["active_mutations"] = ["new_mutation_stub"]
    after["unclaimed_easter_eggs"] = ["mark_initial", "mark_new"]
    after["residue_history"].append({"id": "res2"})
    return after

# --- Test snapshot_floor_memory ---
def test_snapshot_floor_memory_success(mock_floor_memory_before):
    result = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_before)
    assert result["ok"] is True
    snapshot = result["payload"]
    assert snapshot["floor_id"] == 1
    assert snapshot["mutation_level"] == 0
    assert snapshot["active_mutations"] == []
    assert snapshot["residue_history_count"] == 1

def test_snapshot_floor_memory_invalid_input():
    result = replay_floor_diff_reporter.snapshot_floor_memory({"floor_id_missing": 1})
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test diff_floor_snapshots ---
def test_diff_floor_snapshots_no_change(mock_floor_memory_before):
    before_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_before)["payload"]
    after_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_before)["payload"]
    result = replay_floor_diff_reporter.diff_floor_snapshots(before_snap, after_snap)
    assert result["ok"] is True
    assert result["payload"]["changed"] is False
    assert result["payload"]["diff"]["mutation_level_delta"] == 0

def test_diff_floor_snapshots_with_mutation(mock_floor_memory_before, mock_floor_memory_after_mutation):
    before_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_before)["payload"]
    after_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_after_mutation)["payload"]
    result = replay_floor_diff_reporter.diff_floor_snapshots(before_snap, after_snap)
    assert result["ok"] is True
    assert result["payload"]["changed"] is True
    assert result["payload"]["diff"]["mutation_level_delta"] == 1
    assert "new_mutation_stub" in result["payload"]["diff"]["new_active_mutations"]
    assert "mark_new" in result["payload"]["diff"]["new_unclaimed_survivor_marks"]
    assert result["payload"]["diff"]["residue_history_delta"] == 1

def test_diff_floor_snapshots_mismatched_floor_id():
    before_snap = {"floor_id": 1}
    after_snap = {"floor_id": 2}
    result = replay_floor_diff_reporter.diff_floor_snapshots(before_snap, after_snap)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test make_replay_floor_diff_report ---
def test_make_replay_floor_diff_report_success(mock_floor_memory_before, mock_floor_memory_after_mutation):
    result = replay_floor_diff_reporter.make_replay_floor_diff_report(mock_floor_memory_before, mock_floor_memory_after_mutation)
    assert result["ok"] is True
    report = result["payload"]
    assert report["floor_id"] == 1
    assert report["changed"] is True
    assert "mutation_level increased by 1." in report["readable_summary"]
    assert any("New unclaimed survivor marks detected: mark_new." in s for s in report["readable_summary"])

def test_make_replay_floor_diff_report_invalid_floor_id_mismatch():
    before = {"floor_id": 1}
    after = {"floor_id": 2}
    result = replay_floor_diff_reporter.make_replay_floor_diff_report(before, after)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test write_replay_floor_diff_report ---
def test_write_replay_floor_diff_report_success(setup_teardown_test_dir, mock_floor_memory_before, mock_floor_memory_after_mutation):
    report_result = replay_floor_diff_reporter.make_replay_floor_diff_report(mock_floor_memory_before, mock_floor_memory_after_mutation)
    assert report_result["ok"]
    report = report_result["payload"]
    output_path = os.path.join(TEST_DIR, "diff_report.json")
    write_result = replay_floor_diff_reporter.write_replay_floor_diff_report(report, output_path)
    assert write_result["ok"] is True
    assert os.path.exists(output_path)
    
    loaded_report = json_save_manager.load_json(output_path)["payload"]
    assert loaded_report["floor_id"] == 1

# --- Test summarize_replay_floor_diff ---
def test_summarize_replay_floor_diff_content(mock_floor_memory_before, mock_floor_memory_after_mutation):
    before_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_before)["payload"]
    after_snap = replay_floor_diff_reporter.snapshot_floor_memory(mock_floor_memory_after_mutation)["payload"]
    diff_result = replay_floor_diff_reporter.diff_floor_snapshots(before_snap, after_snap)["payload"]["diff"]
    
    summary_result = replay_floor_diff_reporter.summarize_replay_floor_diff(diff_result)
    assert summary_result["ok"] is True
    summary_lines = summary_result["payload"]
    assert "Mutation level increased by 1." in summary_lines
    assert "New active mutations: new_mutation_stub." in summary_lines
    assert "New unclaimed survivor marks detected: mark_new." in summary_lines
    assert "Residue history count increased by 1." in summary_lines
    assert "Floor identity appears preserved (conceptual check)." in summary_lines

# --- Test debug logging ---
@patch('engine.reports.runtime.replay_floor_diff_reporter._debug_logger_available', True)
@patch('engine.reports.runtime.replay_floor_diff_reporter.debug_logger.write_debug_event')
@patch('engine.reports.runtime.replay_floor_diff_reporter.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_reporter_debug_logging(mock_make_event, mock_write_event, mock_floor_memory_before, mock_floor_memory_after_mutation):
    replay_floor_diff_reporter.make_replay_floor_diff_report(mock_floor_memory_before, mock_floor_memory_after_mutation, debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("MakeDiffReport" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.reports.runtime.replay_floor_diff_reporter._debug_logger_available', False)
@patch('builtins.print')
def test_reporter_functional_without_debug_logger(mock_print, mock_floor_memory_before, mock_floor_memory_after_mutation):
    result = replay_floor_diff_reporter.make_replay_floor_diff_report(mock_floor_memory_before, mock_floor_memory_after_mutation, debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Generating replay floor diff report.")