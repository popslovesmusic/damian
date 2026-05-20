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

from engine.residue.runtime import mvp_residue_writer
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper # To get a valid tower_state


# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
RESIDUE_RECORD_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/residue_record.schema.json")
FLOOR_MEMORY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_residue_writer_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # Create dummy schema files for validation
    dummy_residue_schema = {
        "type": "object",
        "properties": {
            "residue_id": {"type": "string"},
            "floor_id": {"type": "integer", "minimum": 1},
            "outcome": {"type": "string"},
            "dominant_damage_type": {"type": "string"},
            "most_used_skill": {"type": "string"},
            "clear_time_seconds": {"type": "number", "minimum": 0},
            "exploration_percent": {"type": "number", "minimum": 0.0, "maximum": 100.0},
            "party_size": {"type": "integer", "minimum": 1},
            "death_event": {"type": "boolean"},
            "mutation_triggered": {"type": "boolean"},
            "notes": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["residue_id", "floor_id", "outcome", "dominant_damage_type", "most_used_skill", "clear_time_seconds", "exploration_percent", "party_size", "death_event", "mutation_triggered", "notes"]
    }
    os.makedirs(os.path.dirname(RESIDUE_RECORD_SCHEMA_PATH), exist_ok=True)
    with open(RESIDUE_RECORD_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_residue_schema, f)

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
            "residue_history": {"type": "array", "items": {"$ref": "residue_record.schema.json"}} # Reference
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
    with patch('engine.residue.runtime.mvp_residue_writer._debug_logger_available', True):
        with patch('engine.residue.runtime.mvp_residue_writer.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Tower State ---
@pytest.fixture
def mock_tower_state():
    return tower_state_bootstrapper.make_default_tower_state()


# --- Test make_residue_record ---
def test_make_residue_record_victory():
    result = mvp_residue_writer.make_residue_record(1, "VICTORY_ASCEND")
    assert result["ok"] is True
    record = result["payload"]
    assert record["floor_id"] == 1
    assert record["outcome"] == "VICTORY_ASCEND"
    assert record["death_event"] is False
    assert record["mutation_triggered"] is False
    assert "residue_id" in record
    
    # Validate against schema
    validation_result = json_save_manager.validate_json(record, RESIDUE_RECORD_SCHEMA_PATH)
    assert validation_result["ok"] is True

def test_make_residue_record_defeat():
    result = mvp_residue_writer.make_residue_record(1, "DEFEAT_DROP")
    assert result["ok"] is True
    record = result["payload"]
    assert record["floor_id"] == 1
    assert record["outcome"] == "DEFEAT_DROP"
    assert record["death_event"] is True
    assert record["mutation_triggered"] is True # This is crucial for defeat
    
    # Validate against schema
    validation_result = json_save_manager.validate_json(record, RESIDUE_RECORD_SCHEMA_PATH)
    assert validation_result["ok"] is True

def test_make_residue_record_invalid_floor_id():
    result = mvp_residue_writer.make_residue_record(0, "VICTORY_ASCEND")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

def test_make_residue_record_invalid_outcome():
    result = mvp_residue_writer.make_residue_record(1, "")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test get_or_create_floor_memory ---
def test_get_or_create_floor_memory_create_new(mock_tower_state):
    result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert result["ok"] is True
    assert len(mock_tower_state["floor_memory"]) == 1
    assert mock_tower_state["floor_memory"][0]["floor_id"] == 1
    assert mock_tower_state["floor_memory"][0]["visit_count"] == 0 # Initialized to 0
    assert mock_tower_state["floor_memory"][0]["mutation_level"] == 0
    
    # Validate created floor memory
    validation_result = json_save_manager.validate_json(mock_tower_state["floor_memory"][0], FLOOR_MEMORY_SCHEMA_PATH)
    assert validation_result["ok"] is True

def test_get_or_create_floor_memory_get_existing(mock_tower_state):
    mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1) # Create once
    result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1) # Get again
    assert result["ok"] is True
    assert len(mock_tower_state["floor_memory"]) == 1 # Should not create duplicate

# --- Test write_residue_to_tower_state ---
def test_write_residue_to_tower_state_victory(mock_tower_state):
    residue = mvp_residue_writer.make_residue_record(1, "VICTORY_ASCEND")["payload"]
    result = mvp_residue_writer.write_residue_to_tower_state(mock_tower_state, residue)
    assert result["ok"] is True
    fm = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)["payload"]
    assert fm["visit_count"] == 1
    assert fm["victory_count"] == 1
    assert fm["death_count"] == 0
    assert fm["mutation_level"] == 0
    assert "mvp_defeat_mutation" not in fm["active_mutations"]
    assert len(fm["residue_history"]) == 1
    assert fm["residue_history"][0] == residue

def test_write_residue_to_tower_state_defeat(mock_tower_state):
    residue = mvp_residue_writer.make_residue_record(1, "DEFEAT_DROP")["payload"]
    result = mvp_residue_writer.write_residue_to_tower_state(mock_tower_state, residue)
    assert result["ok"] is True
    fm = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)["payload"]
    assert fm["visit_count"] == 1
    assert fm["victory_count"] == 0
    assert fm["death_count"] == 1
    assert fm["mutation_level"] == 1 # Increased for defeat
    assert "mvp_defeat_mutation" in fm["active_mutations"]
    assert len(fm["residue_history"]) == 1
    assert fm["residue_history"][0] == residue

# --- Test write_mvp_outcome_residue ---
def test_write_mvp_outcome_residue_success(mock_tower_state):
    result = mvp_residue_writer.write_mvp_outcome_residue(mock_tower_state, 1, "VICTORY_ASCEND")
    assert result["ok"] is True
    assert result["payload"]["tower_state"] is mock_tower_state # Should be the same object
    assert result["payload"]["residue_record"] is not None
    assert result["payload"]["floor_memory"]["floor_id"] == 1
    
    fm = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)["payload"]
    assert fm["visit_count"] == 1
    assert fm["victory_count"] == 1

def test_write_mvp_outcome_residue_invalid_outcome(mock_tower_state):
    result = mvp_residue_writer.write_mvp_outcome_residue(mock_tower_state, 1, "UNKNOWN_OUTCOME")
    assert result["ok"] is False
    assert result["error_type"] == "ResidueSchemaValidationFailure"

def test_write_mvp_outcome_residue_invalid_tower_state():
    invalid_tower_state = {"missing_floor_memory": True}
    result = mvp_residue_writer.write_mvp_outcome_residue(invalid_tower_state, 1, "VICTORY_ASCEND")
    assert result["ok"] is False
    assert result["error_type"] == "WriteResidueError"

# --- Test debug logging ---
@patch('engine.residue.runtime.mvp_residue_writer._debug_logger_available', True)
@patch('engine.residue.runtime.mvp_residue_writer.debug_logger.write_debug_event')
@patch('engine.residue.runtime.mvp_residue_writer.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_residue_writer_debug_logging(mock_make_event, mock_write_event, mock_tower_state):
    mvp_residue_writer.write_mvp_outcome_residue(mock_tower_state, 1, "DEFEAT_DROP", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    # Check for specific event type
    # Check that any call's arguments contain "ResidueRecordCreated"
    assert any("ResidueRecordCreated" in call.args for call in mock_make_event.call_args_list)

@patch('engine.residue.runtime.mvp_residue_writer._debug_logger_available', False)
@patch('builtins.print')
def test_residue_writer_functional_without_debug_logger(mock_print, mock_tower_state):
    result = mvp_residue_writer.write_mvp_outcome_residue(mock_tower_state, 1, "VICTORY_ASCEND", debug=True)
    assert result["ok"] is True
    # Check that warning is printed when debug is true but logger unavailable
    # The actual log message includes the floor and outcome, check for that.
    assert any("WARNING: Debugging is enabled but debug_logger is unavailable." in call.args[0] for call in mock_print.call_args_list)