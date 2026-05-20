import pytest
import os
import json
import shutil
import datetime
import sys
from unittest.mock import patch, mock_open, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.domain.bootstrap import domain_state_bootstrapper
from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DOMAIN_STATE_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/domain/contracts/domain_state.schema.json")
EXAMPLE_DOMAIN_STATE_PATH = os.path.join(PROJECT_ROOT, "engine/domain/contracts/example_domain_state.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_domain_bootstrapper_dir"

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
    mock_dl = MagicMock()
    with patch('engine.domain.bootstrap.domain_state_bootstrapper._debug_logger_available', True):
        with patch('engine.domain.bootstrap.domain_state_bootstrapper.debug_logger', mock_dl):
            yield mock_dl

# --- Test make_default_domain_state ---
def test_make_default_domain_state_validity():
    default_domain = domain_state_bootstrapper.make_default_domain_state()
    assert default_domain["conquered"] is False
    assert default_domain["dashboard_unlocked"] is False
    assert default_domain["domain_level"] == 1
    assert default_domain["stability"] == 1.0
    assert default_domain["deviation"] == 0.0
    assert default_domain["active_modifiers"] == []
    assert all(v == 0 for v in default_domain["operational_costs"].values())
    assert all(v is False for v in default_domain["forbidden_flags"].values())
    assert "domain_state_default_" in default_domain["domain_state_id"]
    
    # Also validate against the actual schema
    schema_load_result = json_save_manager.load_json(DOMAIN_STATE_SCHEMA_PATH)
    assert schema_load_result["ok"] is True
    
    validation_result = json_save_manager.validate_json(default_domain, DOMAIN_STATE_SCHEMA_PATH)
    assert validation_result["ok"] is True, f"Default domain failed schema validation: {validation_result.get('message')}"

# --- Test load_domain_state ---
def test_load_domain_state_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "valid_domain_state.json")
    if os.path.exists(EXAMPLE_DOMAIN_STATE_PATH):
        example_domain_result = json_save_manager.load_json(EXAMPLE_DOMAIN_STATE_PATH)
        assert example_domain_result["ok"]
        example_domain = example_domain_result["payload"]
    else:
        example_domain = domain_state_bootstrapper.make_default_domain_state()
    
    json_save_manager.save_json(test_save_path, example_domain)

    result = domain_state_bootstrapper.load_domain_state(test_save_path)
    assert result["ok"] is True
    assert result["payload"] == example_domain

def test_load_domain_state_file_not_found(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "non_existent.json")
    result = domain_state_bootstrapper.load_domain_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"

def test_load_domain_state_invalid_json(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid.json")
    with open(test_save_path, 'w') as f:
        f.write("{broken json}")
    result = domain_state_bootstrapper.load_domain_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidJson"

def test_load_domain_state_invalid_schema_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_schema_data.json")
    invalid_domain = domain_state_bootstrapper.make_default_domain_state()
    invalid_domain["domain_level"] = "one" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_domain)
    
    result = domain_state_bootstrapper.load_domain_state(test_save_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"

# --- Test save_domain_state ---
def test_save_domain_state_success(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "saved_domain_state.json")
    valid_domain = domain_state_bootstrapper.make_default_domain_state()
    
    result = domain_state_bootstrapper.save_domain_state(test_save_path, valid_domain)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    loaded_result = json_save_manager.load_json(test_save_path)
    assert loaded_result["ok"]
    assert loaded_result["payload"]["domain_level"] == 1

def test_save_domain_state_invalid_data(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_save_data.json")
    invalid_domain = {"not_a_valid_domain": True}
    
    result = domain_state_bootstrapper.save_domain_state(test_save_path, invalid_domain)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    assert not os.path.exists(test_save_path) # Should not save invalid data

# --- Test bootstrap_domain_state ---
def test_bootstrap_domain_state_create_if_missing(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "new_domain_save.json")
    result = domain_state_bootstrapper.bootstrap_domain_state(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    assert result["payload"]["domain_level"] == 1 # Check default attributes

def test_bootstrap_domain_state_file_not_found_no_create(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_create_save.json")
    result = domain_state_bootstrapper.bootstrap_domain_state(test_save_path, create_if_missing=False)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"
    assert not os.path.exists(test_save_path)

def test_bootstrap_domain_state_load_existing_valid(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "existing_valid_save.json")
    existing_domain = domain_state_bootstrapper.make_default_domain_state()
    existing_domain["domain_level"] = 5 # Modify to check if loaded
    json_save_manager.save_validated_json(test_save_path, existing_domain, DOMAIN_STATE_SCHEMA_PATH)

    result = domain_state_bootstrapper.bootstrap_domain_state(test_save_path, create_if_missing=True)
    assert result["ok"] is True
    assert result["payload"]["domain_level"] == 5

def test_bootstrap_domain_state_invalid_existing_save(setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "invalid_existing_save.json")
    invalid_domain = domain_state_bootstrapper.make_default_domain_state()
    invalid_domain["domain_level"] = "not_a_number" # Make it invalid
    json_save_manager.save_json(test_save_path, invalid_domain) # Save invalid JSON directly

    result = domain_state_bootstrapper.bootstrap_domain_state(test_save_path, create_if_missing=True) # Should try to load then validate
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    
def test_bootstrap_domain_state_debug_logging(mock_debug_logger, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "debug_bootstrap.json")
    domain_state_bootstrapper.bootstrap_domain_state(test_save_path, debug=True)
    # Check that debug_logger.make_debug_event and write_debug_event were called
    assert mock_debug_logger.make_debug_event.called
    assert mock_debug_logger.write_debug_event.called

@patch('engine.domain.bootstrap.domain_state_bootstrapper._debug_logger_available', False)
@patch('builtins.print')
def test_bootstrapper_functional_without_debug_logger(mock_print, setup_teardown_test_dir):
    test_save_path = os.path.join(TEST_DIR, "no_logger_bootstrap.json")
    result = domain_state_bootstrapper.bootstrap_domain_state(test_save_path, debug=True)
    assert result["ok"] is True
    assert os.path.exists(test_save_path)
    # Check that warning is printed when debug is true but logger unavailable
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Bootstrapping domain state for {}.".format(test_save_path))