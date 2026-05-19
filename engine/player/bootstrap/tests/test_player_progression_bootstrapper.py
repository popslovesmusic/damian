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

from engine.player.bootstrap import player_progression_bootstrapper
from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PLAYER_PROGRESSION_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/player/contracts/player_progression_state.schema.json")
EXAMPLE_PLAYER_PROGRESSION_PATH = os.path.join(PROJECT_ROOT, "engine/player/contracts/example_player_progression_state.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_player_progression_bootstrapper_dir"

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
    with patch('engine.player.bootstrap.player_progression_bootstrapper._debug_logger_available', True):
        with patch('engine.player.bootstrap.player_progression_bootstrapper.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Test make_default_player_progression ---
def test_make_default_player_progression_validity():
    default_progression = player_progression_bootstrapper.make_default_player_progression()
    assert default_progression["level"] == 1
    assert default_progression["highest_floor_reached"] == 1
    assert default_progression["stats"]["health"] == 100.0
    assert default_progression["stats"]["damage"] == 10.0
    assert default_progression["forbidden_flags"]["permanent_invulnerability"] is False
    assert "player_default_001_" in default_progression["player_id"]
    
    # Also validate against the actual schema
    schema_load_result = json_save_manager.load_json(PLAYER_PROGRESSION_SCHEMA_PATH)
    assert schema_load_result["ok"] is True
    
    validation_result = json_save_manager.validate_json(default_progression, PLAYER_PROGRESSION_SCHEMA_PATH)
    assert validation_result["ok"] is True, f"Default progression failed schema validation: {validation_result.get('message')}"

# --- Test load_player_progression ---
def test_load_player_progression_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "valid_progression.json")
    example_progression_result = json_save_manager.load_json(EXAMPLE_PLAYER_PROGRESSION_PATH)
    assert example_progression_result["ok"]
    example_progression = example_progression_result["payload"]
    
    json_save_manager.save_json(test_save_path, example_progression)

    result = player_progression_bootstrapper.load_player_progression(test_save_path)
    assert result["ok"] is True
    assert result["payload"] == example_progression

def test_load_player_progression_file_not_found(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "non_existent.json")
    result = player_progression_bootstrapper.load_player_progression(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"

def test_load_player_progression_invalid_json(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid.json")
    with open(test_save_path, 'w') as f:
        f.write("{broken json}")
    result = player_progression_bootstrapper.load_player_progression(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidJson"

def test_load_player_progression_invalid_schema_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_schema_data.json")
    invalid_progression = player_progression_bootstrapper.make_default_player_progression()
    invalid_progression["level"] = "one" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_progression)
    
    result = player_progression_bootstrapper.load_player_progression(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"

# --- Test save_player_progression ---
def test_save_player_progression_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "saved_progression.json")
    valid_progression = player_progression_bootstrapper.make_default_player_progression()
    
    result = player_progression_bootstrapper.save_player_progression(test_save_path, valid_progression)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    loaded_result = json_save_manager.load_json(test_save_path)
    assert loaded_result["ok"]
    assert loaded_result["payload"]["level"] == 1

def test_save_player_progression_invalid_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_save_data.json")
    invalid_progression = {"not_a_valid_progression": True}
    
    result = player_progression_bootstrapper.save_player_progression(test_save_path, invalid_progression)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    assert not os.path.exists(test_save_path) # Should not save invalid data

# --- Test bootstrap_player_progression ---
def test_bootstrap_player_progression_create_if_missing(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "new_player_save.json")
    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    assert result["payload"]["level"] == 1 # Check default attributes

def test_bootstrap_player_progression_file_not_found_no_create(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_create_save.json")
    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=False)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"
    assert not os.path.exists(test_save_path)

def test_bootstrap_player_progression_load_existing_valid(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "existing_valid_save.json")
    existing_progression = player_progression_bootstrapper.make_default_player_progression()
    existing_progression["level"] = 10 # Modify to check if loaded
    json_save_manager.save_validated_json(test_save_path, existing_progression, PLAYER_PROGRESSION_SCHEMA_PATH)

    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert result["payload"]["level"] == 10

def test_bootstrap_player_progression_invalid_existing_save(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_existing_save.json")
    invalid_progression = player_progression_bootstrapper.make_default_player_progression()
    invalid_progression["level"] = "not_a_number" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_progression) # Save invalid JSON directly

    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, create_if_missing=True) # Should try to load then validate
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    
def test_bootstrap_player_progression_debug_logging(mock_debug_logger, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "debug_bootstrap.json")
    player_progression_bootstrapper.bootstrap_player_progression(test_save_path, debug=True)
    # Check that debug_logger.make_debug_event and write_debug_event were called
    assert mock_debug_logger.make_debug_event.called
    assert mock_debug_logger.write_debug_event.called

@patch('engine.player.bootstrap.player_progression_bootstrapper._debug_logger_available', False)
@patch('builtins.print')
def test_bootstrapper_functional_without_debug_logger(mock_print, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_logger_bootstrap.json")
    result = player_progression_bootstrapper.bootstrap_player_progression(test_save_path, debug=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    # Check that warning is printed when debug is true but logger unavailable
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Bootstrapping player progression for {}.".format(test_save_path))