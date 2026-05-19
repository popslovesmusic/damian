import pytest
import os
import json
import shutil
import sys
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.core.orchestrator import mvp_startup_orchestrator
from engine.core.runtime import state_machine_driver
from engine.save.bootstrap import tower_state_bootstrapper
from engine.player.bootstrap import player_progression_bootstrapper
from engine.domain.bootstrap import domain_state_bootstrapper
from engine.save.runtime import json_save_manager

# Define a temporary directory for tests
TEST_DIR = "test_temp_orchestrator_dir"
LOCAL_MVP_SAVE_DIR = os.path.join(TEST_DIR, "saves/local_mvp")

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
    with patch('engine.core.orchestrator.mvp_startup_orchestrator._debug_logger_available', True):
        with patch('engine.core.orchestrator.mvp_startup_orchestrator.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Helper functions to create mock save files ---
def create_valid_mock_tower_state_file(path):
    default_state = tower_state_bootstrapper.make_default_tower_state()
    json_save_manager.save_json(path, default_state)

def create_valid_mock_player_progression_file(path):
    default_progression = player_progression_bootstrapper.make_default_player_progression()
    json_save_manager.save_json(path, default_progression)

def create_valid_mock_domain_state_file(path):
    default_domain = domain_state_bootstrapper.make_default_domain_state()
    json_save_manager.save_json(path, default_domain)

# --- Test make_default_runtime_paths ---
def test_make_default_runtime_paths():
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    assert paths["tower_state"] == os.path.join(LOCAL_MVP_SAVE_DIR, "tower_state.json")
    assert paths["player_progression"] == os.path.join(LOCAL_MVP_SAVE_DIR, "player_progression.json")
    assert paths["domain_state"] == os.path.join(LOCAL_MVP_SAVE_DIR, "domain_state.json")
    assert "game_loop_states.json" in paths["state_machine_states"]

# --- Test startup_mvp_runtime ---
def test_startup_mvp_runtime_clean_start_create_missing(setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    # Mock external dependencies if needed to prevent file system operations that conflict with setup_teardown_test_dir
    # For this test, we expect them to create files, so we don't mock json_save_manager's core logic
    
    # Ensure schemas exist for validation
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    # Create dummy schema files (they don't need to be valid JSON Schema, just exist for json_save_manager)
    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)

    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, create_if_missing=True)
    assert context["ok"] is True
    assert context["state_machine"] is not None
    assert context["state_context"] is not None
    assert context["tower_state"] is not None
    assert context["player_progression"] is not None
    assert context["domain_state"] is not None
    assert os.path.exists(paths["tower_state"])
    assert os.path.exists(paths["player_progression"])
    assert os.path.exists(paths["domain_state"])

def test_startup_mvp_runtime_load_existing(setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    
    # Create dummy schema files
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)

    # Create existing valid save files
    create_valid_mock_tower_state_file(paths["tower_state"])
    create_valid_mock_player_progression_file(paths["player_progression"])
    create_valid_mock_domain_state_file(paths["domain_state"])

    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, create_if_missing=True)
    assert context["ok"] is True
    assert context["tower_state"] is not None
    assert context["player_progression"] is not None
    assert context["domain_state"] is not None

def test_startup_mvp_runtime_missing_save_no_create_fails(setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    
    # Create dummy schema files
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)

    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, create_if_missing=False)
    assert context["ok"] is False
    assert any("FileNotFound" in err["error_type"] for err in context["errors"])

def test_startup_mvp_runtime_invalid_tower_state_fails_safely(setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)

    # Create dummy schema files
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object", "properties": {"current_floor": {"type": "integer"}}, "required": ["current_floor"]}, f) # Make schema strict
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)

    # Create an invalid tower state file
    os.makedirs(os.path.dirname(paths["tower_state"]), exist_ok=True)
    with open(paths["tower_state"], 'w') as f:
        json.dump({"current_floor": "not_an_int"}, f) # Invalid data

    # Create other valid saves to isolate the failure
    create_valid_mock_player_progression_file(paths["player_progression"])
    create_valid_mock_domain_state_file(paths["domain_state"])
    
    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, create_if_missing=True)
    assert context["ok"] is False
    assert any("TowerStateBootstrapFailure" in err["error_type"] for err in context["errors"])

def test_startup_mvp_runtime_debug_logging(mock_debug_logger, setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    
    # Create dummy schema files
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)

    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, debug=True)
    assert context["ok"] is True
    assert mock_debug_logger.make_debug_event.called
    assert mock_debug_logger.write_debug_event.called

def test_shutdown_mvp_runtime_success(setup_teardown_test_dir):
    mock_context = {
        "ok": True, "engine_version": "0.0.1", "content_pack_id": "damian",
        "state_machine": {"states": {}, "transitions": []}, "state_context": {"current_state": "SHUTDOWN_ENGINE"},
        "tower_state": {}, "player_progression": {}, "domain_state": {}, "errors": [], "debug_enabled": False
    }
    result = mvp_startup_orchestrator.shutdown_mvp_runtime(mock_context)
    assert result["ok"] is True

@patch('engine.core.orchestrator.mvp_startup_orchestrator._debug_logger_available', False)
@patch('builtins.print')
def test_orchestrator_functional_without_debug_logger(mock_print, setup_teardown_test_dir):
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=LOCAL_MVP_SAVE_DIR)
    
    # Create dummy schema files
    os.makedirs(os.path.dirname(paths["state_machine_states"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["state_machine_transitions"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["tower_state_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["player_progression_schema"]), exist_ok=True)
    os.makedirs(os.path.dirname(paths["domain_state_schema"]), exist_ok=True)

    with open(paths["state_machine_states"], 'w') as f: json.dump({"states": []}, f)
    with open(paths["state_machine_transitions"], 'w') as f: json.dump({"transitions": []}, f)
    with open(paths["tower_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["player_progression_schema"], 'w') as f: json.dump({"type": "object"}, f)
    with open(paths["domain_state_schema"], 'w') as f: json.dump({"type": "object"}, f)
    
    context = mvp_startup_orchestrator.startup_mvp_runtime(paths=paths, debug=True)
    assert context["ok"] is True
    assert any("WARNING: Debugging is enabled but debug_logger is unavailable." in call[0][0] for call in mock_print.call_args_list)