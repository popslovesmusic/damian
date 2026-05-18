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
from engine.easter_eggs.runtime import mvp_survivor_mark_system # For mocking where needed


# Define a temporary directory for tests
TEST_DIR = "test_temp_pipeline_survivor_marks_dir"

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

@pytest.fixture
def mock_survivor_mark_result():
    return mvp_survivor_mark_system.make_survivor_mark(1, "mock_residue_id")["payload"]

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_defeat_drop')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.get_or_create_floor_memory')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory')
def test_defeat_drop_attaches_survivor_mark(
    mock_attach_mark, mock_get_floor_memory, mock_make_mark,
    mock_apply_mutation, mock_write_residue, mock_apply_defeat,
    mock_tower_state, mock_progression_result, mock_residue_result,
    mock_mutation_result, mock_survivor_mark_result
):
    mock_progression_result["tower_state"]["current_floor"] = 1 # Simulate drop to floor 1
    mock_progression_result["tower_state"]["previous_floor"] = 2
    mock_progression_result["outcome"] = "DEFEAT_DROP"
    mock_progression_result["current_floor"] = 1

    mock_residue_result["payload"]["residue_record"]["residue_id"] = "mock_residue_id"

    mock_apply_defeat.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    mock_apply_mutation.return_value = mock_mutation_result
    mock_make_mark.return_value = {"ok": True, "payload": mock_survivor_mark_result}
    mock_get_floor_memory.return_value = {"ok": True, "payload": {"floor_id": 1, "unclaimed_easter_eggs": []}}
    mock_attach_mark.return_value = {"ok": True, "payload": {"floor_id": 1, "unclaimed_easter_eggs": [mock_survivor_mark_result["survivor_mark_id"]]}}

    mock_tower_state["current_floor"] = 2 # Start at floor 2 for defeat drop

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "DEFEAT_DROP")
    assert result["ok"] is True
    assert result["outcome"] == "DEFEAT_DROP"
    assert result["mutation_applied"] is True
    assert result["survivor_mark_attached"] is True
    assert result["survivor_mark_result"] == mock_survivor_mark_result
    
    mock_make_mark.assert_called_once_with(1, "mock_residue_id", mark_index=1, debug=False)
    mock_get_floor_memory.assert_called_once_with(mock_tower_state, 1, debug=False)
    mock_attach_mark.assert_called_once_with({"floor_id": 1, "unclaimed_easter_eggs": []}, mock_survivor_mark_result, debug=False)

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_victory_ascend')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
def test_victory_ascend_does_not_attach_survivor_mark(
    mock_make_mark, mock_apply_mutation, mock_write_residue, mock_apply_ascend,
    mock_tower_state, mock_progression_result, mock_residue_result
):
    mock_progression_result["tower_state"]["current_floor"] = 2
    mock_progression_result["outcome"] = "VICTORY_ASCEND"
    mock_apply_ascend.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    
    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "VICTORY_ASCEND")
    assert result["ok"] is True
    assert result["mutation_applied"] is False
    assert result["survivor_mark_attached"] is False
    mock_make_mark.assert_not_called()

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.resolve_floor_outcome')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
def test_retreat_does_not_attach_survivor_mark(mock_make_mark, *args):
    mock_tower_state_after_retreat = mock_tower_state().copy()
    mock_tower_state_after_retreat["current_floor"] = 1 # No change
    mock_progression_result = {
        "ok": True, "tower_state": mock_tower_state_after_retreat,
        "outcome": "RETREAT_TO_HUB", "error": None
    }
    mock_residue_result = {
        "ok": True, "tower_state": mock_tower_state_after_retreat,
        "residue_record": {"residue_id": "test_retreat_residue", "floor_id": 1, "outcome": "RETREAT_TO_HUB"},
        "floor_memory": {"floor_id": 1}, "error": None
    }

    mvp_outcome_pipeline.mvp_floor_progression.resolve_floor_outcome.return_value = mock_progression_result
    mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue.return_value = mock_residue_result

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state(), "RETREAT_TO_HUB")
    assert result["ok"] is True
    assert result["survivor_mark_attached"] is False
    mock_make_mark.assert_not_called()

@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.resolve_floor_outcome')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
def test_exit_game_does_not_attach_survivor_mark(mock_make_mark, *args):
    mock_tower_state_after_exit = mock_tower_state().copy()
    mock_tower_state_after_exit["current_floor"] = 1
    mock_progression_result = {
        "ok": True, "tower_state": mock_tower_state_after_exit,
        "outcome": "EXIT_GAME", "shutdown_requested": True, "error": None
    }
    mock_residue_result = {
        "ok": True, "tower_state": mock_tower_state_after_exit,
        "residue_record": {"residue_id": "test_exit_residue", "floor_id": 1, "outcome": "EXIT_GAME"},
        "floor_memory": {"floor_id": 1}, "error": None
    }
    mvp_outcome_pipeline.mvp_floor_progression.resolve_floor_outcome.return_value = mock_progression_result
    mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue.return_value = mock_residue_result

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state(), "EXIT_GAME")
    assert result["ok"] is True
    assert result["survivor_mark_attached"] is False
    mock_make_mark.assert_not_called()

# --- Test debug logging ---
@patch('engine.prototype.runtime.mvp_outcome_pipeline._debug_logger_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.debug_logger.write_debug_event')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_defeat_drop')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.get_or_create_floor_memory')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory')
def test_defeat_drop_debug_logging(
    mock_attach_mark, mock_get_floor_memory, mock_make_mark,
    mock_apply_mutation, mock_write_residue, mock_apply_defeat,
    mock_make_event, mock_write_event, mock_tower_state,
    mock_progression_result, mock_residue_result, mock_mutation_result, mock_survivor_mark_result
):
    mock_progression_result["tower_state"]["current_floor"] = 1
    mock_progression_result["outcome"] = "DEFEAT_DROP"
    mock_residue_result["payload"]["residue_record"]["residue_id"] = "mock_residue_id"

    mock_apply_defeat.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    mock_apply_mutation.return_value = mock_mutation_result
    mock_make_mark.return_value = {"ok": True, "payload": mock_survivor_mark_result}
    mock_get_floor_memory.return_value = {"ok": True, "payload": {"floor_id": 1, "unclaimed_easter_eggs": []}}
    mock_attach_mark.return_value = {"ok": True, "payload": {}}

    mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "DEFEAT_DROP", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("DefeatPipeline" in event["args"] for event in mock_make_event.call_args_list)
    assert any("MakeSurvivorMark" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.prototype.runtime.mvp_outcome_pipeline._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_progression_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_residue_writer_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_floor_mutation_stub_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline._mvp_survivor_mark_system_available', True)
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_progression.apply_defeat_drop')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.write_mvp_outcome_residue')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_floor_mutation_stub.apply_replay_floor_mutation_stub')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.make_survivor_mark')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_residue_writer.get_or_create_floor_memory')
@patch('engine.prototype.runtime.mvp_outcome_pipeline.mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory')
def test_pipeline_functional_without_debug_logger(
    mock_attach_mark, mock_get_floor_memory, mock_make_mark,
    mock_apply_mutation, mock_write_residue, mock_apply_defeat,
    mock_print, mock_tower_state, mock_progression_result,
    mock_residue_result, mock_mutation_result, mock_survivor_mark_result
):
    mock_progression_result["tower_state"]["current_floor"] = 1
    mock_progression_result["outcome"] = "DEFEAT_DROP"
    mock_residue_result["payload"]["residue_record"]["residue_id"] = "mock_residue_id"

    mock_apply_defeat.return_value = mock_progression_result
    mock_write_residue.return_value = mock_residue_result
    mock_apply_mutation.return_value = mock_mutation_result
    mock_make_mark.return_value = {"ok": True, "payload": mock_survivor_mark_result}
    mock_get_floor_memory.return_value = {"ok": True, "payload": {"floor_id": 1, "unclaimed_easter_eggs": []}}
    mock_attach_mark.return_value = {"ok": True, "payload": {}}

    result = mvp_outcome_pipeline.resolve_mvp_floor_outcome(mock_tower_state, "DEFEAT_DROP", debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Starting defeat drop pipeline.")