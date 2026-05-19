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

from engine.progression.runtime import mvp_floor_progression

# Define a temporary directory for tests
TEST_DIR = "test_temp_mvp_progression_dir"

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
    with patch('engine.progression.runtime.mvp_floor_progression._debug_logger_available', True):
        with patch('engine.progression.runtime.mvp_floor_progression.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Tower State ---
@pytest.fixture
def mock_tower_state():
    return {
        "tower_state_id": "test_tower",
        "engine_version": "0.0.1",
        "content_pack_id": "damian",
        "current_floor": 1,
        "highest_floor_reached": 1,
        "total_runs": 0,
        "total_deaths": 0,
        "last_outcome": "BOOTSTRAP",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "global_residue": {},
        "floor_memory": []
    }

# --- Test validate_mvp_floor_bounds ---
def test_validate_mvp_floor_bounds_valid(mock_tower_state):
    result = mvp_floor_progression.validate_mvp_floor_bounds(mock_tower_state, max_floor=3)
    assert result["ok"] is True

def test_validate_mvp_floor_bounds_invalid_low(mock_tower_state):
    mock_tower_state["current_floor"] = 0
    result = mvp_floor_progression.validate_mvp_floor_bounds(mock_tower_state, max_floor=3)
    assert result["ok"] is False
    assert result["error_type"] == "FloorOutOfBounds"

def test_validate_mvp_floor_bounds_invalid_high(mock_tower_state):
    mock_tower_state["current_floor"] = 4
    result = mvp_floor_progression.validate_mvp_floor_bounds(mock_tower_state, max_floor=3)
    assert result["ok"] is False
    assert result["error_type"] == "FloorOutOfBounds"

# --- Test apply_victory_ascend ---
def test_apply_victory_ascend_from_floor_1(mock_tower_state):
    result = mvp_floor_progression.apply_victory_ascend(mock_tower_state, max_floor=3)
    assert result["ok"] is True
    assert result["tower_state"]["current_floor"] == 2
    assert result["tower_state"]["highest_floor_reached"] == 2
    assert result["floor_changed"] is True

def test_apply_victory_ascend_from_floor_2(mock_tower_state):
    mock_tower_state["current_floor"] = 2
    mock_tower_state["highest_floor_reached"] = 2
    result = mvp_floor_progression.apply_victory_ascend(mock_tower_state, max_floor=3)
    assert result["ok"] is True
    assert result["tower_state"]["current_floor"] == 3
    assert result["tower_state"]["highest_floor_reached"] == 3
    assert result["floor_changed"] is True

def test_apply_victory_ascend_from_max_floor(mock_tower_state):
    mock_tower_state["current_floor"] = 3
    mock_tower_state["highest_floor_reached"] = 3
    result = mvp_floor_progression.apply_victory_ascend(mock_tower_state, max_floor=3)
    assert result["ok"] is True
    assert result["tower_state"]["current_floor"] == 3
    assert result["tower_state"]["highest_floor_reached"] == 3
    assert result["floor_changed"] is False # Should not change if already at max

# --- Test apply_defeat_drop ---
def test_apply_defeat_drop_from_floor_3(mock_tower_state):
    mock_tower_state["current_floor"] = 3
    mock_tower_state["highest_floor_reached"] = 3
    result = mvp_floor_progression.apply_defeat_drop(mock_tower_state)
    assert result["ok"] is True
    assert result["tower_state"]["current_floor"] == 2
    assert result["tower_state"]["highest_floor_reached"] == 3 # Highest reached is not affected
    assert result["floor_changed"] is True

def test_apply_defeat_drop_from_floor_1(mock_tower_state):
    mock_tower_state["current_floor"] = 1
    mock_tower_state["highest_floor_reached"] = 1
    result = mvp_floor_progression.apply_defeat_drop(mock_tower_state)
    assert result["ok"] is True
    assert result["tower_state"]["current_floor"] == 1 # Stays at 1
    assert result["tower_state"]["highest_floor_reached"] == 1
    assert result["floor_changed"] is False

# --- Test resolve_floor_outcome ---
def test_resolve_floor_outcome_victory(mock_tower_state):
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "VICTORY_ASCEND")
    assert result["ok"] is True
    assert result["outcome"] == "VICTORY_ASCEND"
    assert result["tower_state"]["current_floor"] == 2

def test_resolve_floor_outcome_defeat(mock_tower_state):
    mock_tower_state["current_floor"] = 2
    mock_tower_state["highest_floor_reached"] = 2
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "DEFEAT_DROP")
    assert result["ok"] is True
    assert result["outcome"] == "DEFEAT_DROP"
    assert result["tower_state"]["current_floor"] == 1

def test_resolve_floor_outcome_retreat(mock_tower_state):
    mock_tower_state["current_floor"] = 2
    mock_tower_state["highest_floor_reached"] = 2
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "RETREAT_TO_HUB")
    assert result["ok"] is True
    assert result["outcome"] == "RETREAT_TO_HUB"
    assert result["tower_state"]["current_floor"] == 2
    assert result["floor_changed"] is False

def test_resolve_floor_outcome_exit_game(mock_tower_state):
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "EXIT_GAME")
    assert result["ok"] is True
    assert result["outcome"] == "EXIT_GAME"
    assert result["shutdown_requested"] is True

def test_resolve_floor_outcome_invalid(mock_tower_state):
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "INVALID_OUTCOME")
    assert result["ok"] is False
    assert result["error"]["error_type"] == "InvalidOutcome"

def test_resolve_floor_outcome_invalid_tower_state():
    invalid_tower_state = {"missing_current_floor": 1}
    result = mvp_floor_progression.resolve_floor_outcome(invalid_tower_state, "VICTORY_ASCEND")
    assert result["ok"] is False
    assert result["error"]["error_type"] == "InvalidTowerState"

# --- Test can_enter_floor ---
def test_can_enter_floor_valid(mock_tower_state):
    result = mvp_floor_progression.can_enter_floor(mock_tower_state, 2, max_floor=3)
    assert result["ok"] is True

def test_can_enter_floor_invalid_low(mock_tower_state):
    result = mvp_floor_progression.can_enter_floor(mock_tower_state, 0, max_floor=3)
    assert result["ok"] is False
    assert result["error_type"] == "FloorOutOfBounds"

def test_can_enter_floor_invalid_high(mock_tower_state):
    result = mvp_floor_progression.can_enter_floor(mock_tower_state, 4, max_floor=3)
    assert result["ok"] is False
    assert result["error_type"] == "FloorOutOfBounds"

# --- Test debug logging ---
@patch('engine.progression.runtime.mvp_floor_progression._debug_logger_available', True)
@patch('engine.progression.runtime.mvp_floor_progression.debug_logger.write_debug_event')
@patch('engine.progression.runtime.mvp_floor_progression.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_progression_debug_logging(mock_make_event, mock_write_event, mock_tower_state):
    mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "VICTORY_ASCEND", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    # Check for specific event type
    assert any("VictoryAscend" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.progression.runtime.mvp_floor_progression._debug_logger_available', False)
@patch('builtins.print')
def test_progression_functional_without_debug_logger(mock_print, mock_tower_state):
    result = mvp_floor_progression.resolve_floor_outcome(mock_tower_state, "DEFEAT_DROP", debug=True)
    assert result["ok"] is True
    # Check that warning is printed when debug is true but logger unavailable
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Applying defeat drop.")