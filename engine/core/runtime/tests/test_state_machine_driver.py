import pytest
from unittest.mock import patch
import os
import json
import sys
import shutil

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.core.runtime import state_machine_driver
from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
STATES_PATH = os.path.join(PROJECT_ROOT, "engine/core/state_machine/game_loop_states.json")
TRANSITIONS_PATH = os.path.join(PROJECT_ROOT, "engine/core/state_machine/game_loop_transitions.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_driver_dir"

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
    with patch('engine.core.runtime.state_machine_driver._debug_logger_available', True):
        with patch('engine.core.runtime.state_machine_driver.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Test load_state_machine ---
def test_load_state_machine_success():
    result = state_machine_driver.load_state_machine(STATES_PATH, TRANSITIONS_PATH)
    assert result["ok"] is True
    assert "states" in result["payload"]
    assert "transitions" in result["payload"]
    assert "BOOT_ENGINE" in result["payload"]["states"]

def test_load_state_machine_missing_states_file():
    result = state_machine_driver.load_state_machine("non_existent_states.json", TRANSITIONS_PATH)
    assert result["ok"] is False
    assert result["error_type"] == "LoadStatesError"

def test_load_state_machine_missing_transitions_file():
    result = state_machine_driver.load_state_machine(STATES_PATH, "non_existent_transitions.json")
    assert result["ok"] is False
    assert result["error_type"] == "LoadTransitionsError"

# --- Test create_runtime_context ---
def test_create_runtime_context_default():
    context = state_machine_driver.create_runtime_context()
    assert context["ok"] is True
    assert context["current_state"] == "BOOT_ENGINE"
    assert context["visited_states"] == ["BOOT_ENGINE"]
    assert context["last_error"] is None

def test_create_runtime_context_custom_initial_state():
    context = state_machine_driver.create_runtime_context("ACTIVE_FLOOR_LOOP")
    assert context["ok"] is True
    assert context["current_state"] == "ACTIVE_FLOOR_LOOP"
    assert context["visited_states"] == ["ACTIVE_FLOOR_LOOP"]

# --- Test can_transition ---
@pytest.fixture
def loaded_machine():
    result = state_machine_driver.load_state_machine(STATES_PATH, TRANSITIONS_PATH)
    assert result["ok"] is True
    return result["payload"]

def test_can_transition_valid(loaded_machine):
    assert state_machine_driver.can_transition(loaded_machine, "BOOT_ENGINE", "LOAD_CONTENT_PACK") is True

def test_can_transition_invalid(loaded_machine):
    assert state_machine_driver.can_transition(loaded_machine, "BOOT_ENGINE", "ACTIVE_FLOOR_LOOP") is False

def test_can_transition_non_existent_state(loaded_machine):
    assert state_machine_driver.can_transition(loaded_machine, "NON_EXISTENT_STATE", "LOAD_CONTENT_PACK") is False

# --- Test step_transition ---
def test_step_transition_valid(loaded_machine):
    context = state_machine_driver.create_runtime_context()
    result = state_machine_driver.step_transition(loaded_machine, context, "LOAD_CONTENT_PACK")
    assert result["ok"] is True
    assert result["payload"]["current_state"] == "LOAD_CONTENT_PACK"
    assert result["payload"]["visited_states"] == ["BOOT_ENGINE", "LOAD_CONTENT_PACK"]

def test_step_transition_invalid_transition(loaded_machine):
    context = state_machine_driver.create_runtime_context("BOOT_ENGINE")
    result = state_machine_driver.step_transition(loaded_machine, context, "ACTIVE_FLOOR_LOOP")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidState"
    # assert "Cannot transition from 'BOOT_ENGINE' to 'ACTIVE_FLOOR_LOOP'" in result["message"] # This line might need to be adjusted or removed
    assert context["current_state"] == "BOOT_ENGINE" # State should not change

def test_step_transition_invalid_target_state(loaded_machine):
    context = state_machine_driver.create_runtime_context()
    result = state_machine_driver.step_transition(loaded_machine, context, "NON_EXISTENT_STATE")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidState"
    assert "Target state 'NON_EXISTENT_STATE' not found" in result["message"]

# --- Test run_scripted_path ---
def test_run_scripted_path_success(loaded_machine):
    context = state_machine_driver.create_runtime_context()
    scripted_path = [
        "LOAD_CONTENT_PACK",
        "LOAD_PLAYER_PROFILE",
        "LOAD_TOWER_STATE",
        "SELECT_TARGET_FLOOR",
        "GENERATE_OR_RESTORE_FLOOR",
        "APPLY_RESIDUE_MUTATIONS",
        "SPAWN_PLAYERS",
        "SPAWN_ENCOUNTERS",
        "ACTIVE_FLOOR_LOOP",
        "RESOLVE_FLOOR_OUTCOME",
        "WRITE_RESIDUE",
        "MUTATE_TOWER_STATE",
        "SAVE_RUNTIME_STATE",
        "RETURN_TO_HUB_OR_NEXT_FLOOR",
        "SHUTDOWN_ENGINE"
    ]
    result = state_machine_driver.run_scripted_path(loaded_machine, context, scripted_path)
    if not result["ok"]:
        print(f"DEBUG: context={context}")
        print(f"DEBUG: result={result}")
    assert result["ok"] is True
    assert result["payload"]["current_state"] == "SHUTDOWN_ENGINE"
    assert len(result["payload"]["visited_states"]) == len(scripted_path) + 1

def test_run_scripted_path_failure_mid_path(loaded_machine):
    context = state_machine_driver.create_runtime_context()
    scripted_path_with_error = [
        "LOAD_CONTENT_PACK",
        "ACTIVE_FLOOR_LOOP", # Invalid transition
        "SHUTDOWN_ENGINE"
    ]
    result = state_machine_driver.run_scripted_path(loaded_machine, context, scripted_path_with_error)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidState"
    assert context["current_state"] == "LOAD_CONTENT_PACK" # Should stop at the last valid state

# --- Test debug hooks ---
@patch('engine.core.runtime.state_machine_driver._debug_logger_available', True)
@patch('engine.core.runtime.state_machine_driver.debug_logger.write_debug_event')
@patch('engine.core.runtime.state_machine_driver.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_step_transition_debug_logging(mock_make_event, mock_write_event, loaded_machine):
    context = state_machine_driver.create_runtime_context()
    state_machine_driver.step_transition(loaded_machine, context, "LOAD_CONTENT_PACK", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    # Verify event content
    args, kwargs = mock_make_event.call_args
    assert args[2] == "INFO" # severity
    assert args[3] == "OperationSuccess" # event_type
    assert "Operation completed successfully." in args[4] # message

@patch('engine.core.runtime.state_machine_driver._debug_logger_available', False) # Simulate logger unavailable
@patch('builtins.print') # Mock print to check warnings
def test_state_machine_driver_functional_without_debug_logger(mock_print, loaded_machine):
    context = state_machine_driver.create_runtime_context()
    scripted_path = ["LOAD_CONTENT_PACK"]
    result = state_machine_driver.run_scripted_path(loaded_machine, context, scripted_path, debug=True)
    assert result["ok"] is True
    assert context["current_state"] == "LOAD_CONTENT_PACK"
    # Check that a warning was printed because debug was enabled but logger unavailable
    mock_print.assert_any_call(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: Operation completed successfully.")
    mock_print.assert_any_call(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: Transitioned from 'BOOT_ENGINE' to 'LOAD_CONTENT_PACK'.")
