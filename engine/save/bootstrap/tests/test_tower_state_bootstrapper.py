import pytest
import os
import json
import shutil
import datetime
import sys
from unittest.mock import patch, mock_open

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.save.bootstrap import tower_state_bootstrapper
from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TOWER_STATE_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/tower_state.schema.json")
EXAMPLE_TOWER_STATE_PATH = os.path.join(PROJECT_ROOT, "engine/save/examples/example_tower_state.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_bootstrapper_dir"

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
    with patch('engine.save.bootstrap.tower_state_bootstrapper._debug_logger_available', True):
        with patch('engine.save.bootstrap.tower_state_bootstrapper.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Test make_default_tower_state ---
def test_make_default_tower_state_validity():
    default_state = tower_state_bootstrapper.make_default_tower_state()
    assert default_state["current_floor"] == 1
    assert default_state["highest_floor_reached"] == 1
    assert default_state["total_runs"] == 0
    assert default_state["total_deaths"] == 0
    assert default_state["last_outcome"] == "BOOTSTRAP"
    assert "tower_state_default_" in default_state["tower_state_id"]
    
    # Also validate against the actual schema
    # First, load the schema
    schema_load_result = json_save_manager.load_json(TOWER_STATE_SCHEMA_PATH)
    assert schema_load_result["ok"] is True
    schema = schema_load_result["payload"]

    validation_result = json_save_manager.validate_json(default_state, TOWER_STATE_SCHEMA_PATH)
    assert validation_result["ok"] is True, f"Default state failed schema validation: {validation_result.get('message')}"

# --- Test load_tower_state ---
def test_load_tower_state_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "valid_tower_state.json")
    # Use the example tower state as valid data
    example_state_result = json_save_manager.load_json(EXAMPLE_TOWER_STATE_PATH)
    assert example_state_result["ok"]
    example_state = example_state_result["payload"]
    
    json_save_manager.save_json(test_save_path, example_state)

    result = tower_state_bootstrapper.load_tower_state(test_save_path)
    assert result["ok"] is True
    assert result["payload"] == example_state

def test_load_tower_state_file_not_found(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "non_existent.json")
    result = tower_state_bootstrapper.load_tower_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"

def test_load_tower_state_invalid_json(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid.json")
    with open(test_save_path, 'w') as f:
        f.write("{broken json}")
    result = tower_state_bootstrapper.load_tower_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidJson"

def test_load_tower_state_invalid_schema_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_schema_data.json")
    invalid_state = tower_state_bootstrapper.make_default_tower_state()
    invalid_state["current_floor"] = "one" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_state)
    
    result = tower_state_bootstrapper.load_tower_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"

# --- Test save_tower_state ---
def test_save_tower_state_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "saved_tower_state.json")
    valid_state = tower_state_bootstrapper.make_default_tower_state()
    
    result = tower_state_bootstrapper.save_tower_state(test_save_path, valid_state)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    loaded_result = json_save_manager.load_json(test_save_path)
    assert loaded_result["ok"]
    assert loaded_result["payload"]["current_floor"] == 1

def test_save_tower_state_invalid_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_save_data.json")
    invalid_state = {"not_a_valid_state": True}
    
    result = tower_state_bootstrapper.save_tower_state(test_save_path, invalid_state)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    assert not os.path.exists(test_save_path) # Should not save invalid data

# --- Test bootstrap_tower_state ---
def test_bootstrap_tower_state_create_if_missing(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "new_game_save.json")
    result = tower_state_bootstrapper.bootstrap_tower_state(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    assert result["payload"]["current_floor"] == 1 # Check default attributes

def test_bootstrap_tower_state_file_not_found_no_create(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_create_save.json")
    result = tower_state_bootstrapper.bootstrap_tower_state(test_save_path, create_if_missing=False)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"
    assert not os.path.exists(test_save_path)

def test_bootstrap_tower_state_load_existing_valid(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "existing_valid_save.json")
    existing_state = tower_state_bootstrapper.make_default_tower_state()
    existing_state["current_floor"] = 5 # Modify to check if loaded
    json_save_manager.save_validated_json(test_save_path, existing_state, TOWER_STATE_SCHEMA_PATH)

    result = tower_state_bootstrapper.bootstrap_tower_state(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert result["payload"]["current_floor"] == 5

def test_bootstrap_tower_state_invalid_existing_save(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_existing_save.json")
    invalid_state = tower_state_bootstrapper.make_default_tower_state()
    invalid_state["current_floor"] = "not_a_number" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_state) # Save invalid JSON directly

    result = tower_state_bootstrapper.bootstrap_tower_state(test_save_path, create_if_missing=True) # Should try to load then validate
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    # Should not overwrite with default if existing is invalid and create_if_missing is true, but invalid.
    # The requirement states "invalid save must fail safely", which means return error.
    
def test_bootstrap_tower_state_debug_logging(mock_debug_logger, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "debug_bootstrap.json")
    tower_state_bootstrapper.bootstrap_tower_state(test_save_path, debug=True)
    # Check that debug_logger.make_debug_event and write_debug_event were called
    assert mock_debug_logger.make_debug_event.called
    assert mock_debug_logger.write_debug_event.called

@patch('engine.save.bootstrap.tower_state_bootstrapper._debug_logger_available', False)
@patch('builtins.print')
def test_bootstrapper_functional_without_debug_logger(mock_print, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_logger_bootstrap.json")
    result = tower_state_bootstrapper.bootstrap_tower_state(test_save_path, debug=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    # Check that warning is printed when debug is true but logger unavailable
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Bootstrapping tower state for {}.".format(test_save_path))
