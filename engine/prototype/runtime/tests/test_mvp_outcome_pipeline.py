import pytest
import os
import json
import shutil
import sys
import datetime
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.prototype.runtime import mvp_outcome_pipeline
from engine.save.bootstrap import tower_state_bootstrapper
from engine.progression.runtime import mvp_floor_progression # For mocking where needed
from engine.residue.runtime import mvp_residue_writer # For mocking where needed
from engine.mutation.runtime import mvp_floor_mutation_stub # For mocking where needed


# Define a temporary directory for tests
TEST_DIR = "test_temp_pipeline_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
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
    with patch('engine.prototype.runtime.mvp_outcome_pipeline._debug_logger_available', True):
        with patch('engine.prototype.runtime.mvp_outcome_pipeline.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Tower State ---
@pytest.fixture
def mock_tower_state():
    # Use the bootstrapper to create a valid, clean tower state
    return tower_state_bootstrapper.make_default_tower_state()

# --- Mock Results from sub-modules ---
@pytest.fixture
def mock_progression_result(mock_tower_state):
    return {
        "ok": True,
        "tower_state": mock_tower_state,
        "outcome": "VICTORY_ASCEND",
        "previous_floor": 1,
        "current_floor": 2,
        "highest_floor_reached": 2,
        "floor_changed": True,
        "shutdown_requested": False,
        "error": None
    }

@pytest.fixture
def mock_residue_result(mock_tower_state):
    return {
        "ok": True,
        "tower_state": mock_tower_state,
        "residue_record": {"residue_id": "test_residue", "floor_id": 1, "outcome": "VICTORY_ASCEND"},
        "floor_memory": {"floor_id": 1, "visit_count": 1, "victory_count": 1},
        "error": None
    }

@pytest.fixture
def mock_mutation_result(mock_tower_state):
    return {
        "ok": True,
        "tower_state": mock_tower_state,
        "mutation_event": {"mutation_event_id": "test_mutation_event"},
        "error": None
    }

# --- Test resolve_mvp_floor_outcome (integration with mocks) ---
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_victory_ascend')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
def test_resolve_mvp_floor_outcome_victory(
    mock_write_residue, mock_apply_ascend, mock_tower_state, mock_progression_result, mock_residue_result
):
    mock_apply_ascend.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "VICTORY_ASCEND")
    assert result["ok"] is True
    assert result["outcome"] == "VICTORY_ASCEND"
    assert result["current_floor"] == 2
    assert result["mutation_applied"] is False
    mock_apply_ascend.assert_called_once()
    mock_write_residue.assert_called_once_with(mock_tower_state, 1, "VICTORY_ASCEND", debug=False) # previous_floor

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_defeat_drop')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
def test_resolve_mvp_floor_outcome_defeat_drop(
    mock_apply_mutation, mock_write_residue, mock_apply_defeat, mock_tower_state,
    mock_progression_result, mock_residue_result, mock_mutation_result
):
    mock_progression_result["tower_state"]["current_floor"] = 1 # Simulate drop to floor 1
    mock_progression_result["tower_state"]["previous_floor"] = 2
    mock_progression_result["outcome"] = "DEFEAT_DROP"
    mock_progression_result["current_floor"] = 1

    mock_residue_result["payload"]["residue_record"]["residue_id"] = "mock_residue_id"

    mock_apply_defeat.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    mock_apply_mutation.return_value = mock_mutation_result

    mock_tower_state["current_floor"] = 2 # Start at floor 2 for defeat drop

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "DEFEAT_DROP")
    assert result["ok"] is True
    assert result["outcome"] == "DEFEAT_DROP"
    assert result["current_floor"] == 1
    assert result["mutation_applied"] is True
    mock_apply_defeat.assert_called_once()
    mock_write_residue.assert_called_once_with(mock_tower_state, 1, "DEFEAT_DROP", debug=False) # current_floor
    mock_apply_mutation.assert_called_once_with(mock_tower_state, 1, "mock_residue_id", debug=False)

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.resolve_floor_outcome')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
def test_resolve_mvp_floor_outcome_retreat(mock_write_residue, mock_progression_resolve, mock_tower_state, mock_progression_result, mock_residue_result):
    mock_progression_result["outcome"] = "RETREAT_TO_HUB"
    mock_progression_resolve.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    
    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "RETREAT_TO_HUB")
    assert result["ok"] is True
    assert result["outcome"] == "RETREAT_TO_HUB"
    assert result["mutation_applied"] is False
    mock_progression_resolve.assert_called_once_with(mock_tower_state, "RETREAT_TO_HUB", debug=False)
    mock_write_residue.assert_called_once_with(mock_tower_state, mock_tower_state["current_floor"], "RETREAT_TO_HUB", debug=False)

def test_resolve_mvp_floor_outcome_invalid_outcome(mock_tower_state):
    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "INVALID_OUTCOME")
    assert result["ok"] is False
    assert result["error"]["error_type"] == "InvalidOutcome"

def test_resolve_mvp_floor_outcome_progression_fails(mock_tower_state):
    with patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True):
        with patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_victory_ascend') as mock_apply_ascend:
            mock_apply_ascend.return_value = {"ok": False, "error": {"message": "Progression error"}}
            result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "VICTORY_ASCEND")
            assert result["ok"] is False
            assert result["error"]["error_type"] == "ProgressionFailure"

# --- Test debug logging ---
@patch('engine.prototype.runtime.mvp_outcome_pipeline._debug_logger_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.debug_logger.write_debug_event')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_victory_ascend')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
def test_pipeline_debug_logging(mock_write_residue, mock_apply_ascend, mock_make_event, mock_write_event, mock_tower_state, mock_progression_result, mock_residue_result):
    mock_apply_ascend.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    
    mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "VICTORY_ASCEND", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("VictoryPipeline" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.prototype.runtime.mvp_outcome_pipeline._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_victory_ascend')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
def test_pipeline_functional_without_debug_logger(
    mock_write_residue, mock_apply_ascend, mock_print, mock_tower_state, mock_progression_result, mock_residue_result
):
    mock_apply_ascend.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "VICTORY_ASCEND", debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Starting victory pipeline.")