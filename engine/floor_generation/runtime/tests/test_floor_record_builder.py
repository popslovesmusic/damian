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

from engine.floor_generation.runtime import floor_record_builder
from engine.save.runtime import json_save_manager

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FLOOR_MEMORY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
FLOOR_IDENTITY_RULES_PATH = os.path.join(PROJECT_ROOT, "engine/floor_generation/identity/floor_identity_preservation_rules.json")

# Define a temporary directory for tests
TEST_DIR = "test_temp_floor_record_builder_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    
    # Create dummy identity rules file for tests
    dummy_identity_rules = {
        "required_identity_anchors": [
            {"anchor_id": "layout_seed_lineage"},
            {"anchor_id": "entry_exit_continuity"},
            {"anchor_id": "primary_route_survivability"},
            {"anchor_id": "landmark_continuity"},
            {"anchor_id": "floor_theme_continuity"},
            {"anchor_id": "difficulty_bounds"},
            {"anchor_id": "secret_discoverability"}
        ]
    }
    os.makedirs(os.path.dirname(FLOOR_IDENTITY_RULES_PATH), exist_ok=True)
    with open(FLOOR_IDENTITY_RULES_PATH, 'w') as f:
        json.dump(dummy_identity_rules, f)

    # Create dummy floor memory schema file for validation tests
    dummy_floor_memory_schema = {
        "type": "object",
        "properties": {
            "floor_id": {"type": "integer", "minimum": 1},
            "content_pack_id": {"type": "string"},
            "domain_archetype": {"type": "string"},
            "layout_seed": {"type": "string"},
            "seed_lineage": {"type": "string"},
            "identity_anchors": {"type": "array", "items": {"type": "string"}},
            "mutation_level": {"type": "integer", "minimum": 0},
            "active_mutations": {"type": "array", "items": {"type": "string"}},
            "playability_status": {"type": "string", "enum": ["UNGENERATED_VALID"]}
        },
        "required": ["floor_id", "content_pack_id", "domain_archetype", "layout_seed", "seed_lineage", "identity_anchors", "mutation_level", "active_mutations", "playability_status"]
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
    with patch('engine.floor_generation.runtime.floor_record_builder._debug_logger_available', True):
        with patch('engine.floor_generation.runtime.floor_record_builder.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Test make_floor_seed ---
def test_make_floor_seed_deterministic():
    seed1 = floor_record_builder.make_floor_seed("damian", 1, "tower_domain", "run_a")
    seed2 = floor_record_builder.make_floor_seed("damian", 1, "tower_domain", "run_a")
    assert seed1 == seed2

def test_make_floor_seed_differs_for_different_inputs():
    seed1 = floor_record_builder.make_floor_seed("damian", 1, "tower_domain", "run_a")
    seed2 = floor_record_builder.make_floor_seed("damian", 2, "tower_domain", "run_a")
    assert seed1 != seed2
    seed3 = floor_record_builder.make_floor_seed("jacobs_bane", 1, "swamp_domain", "run_a")
    assert seed1 != seed3

# --- Test make_floor_record ---
def test_make_floor_record_success():
    result = floor_record_builder.make_floor_record(1)
    assert result["ok"] is True
    record = result["payload"]
    assert record["floor_id"] == 1
    assert record["content_pack_id"] == "damian"
    assert record["domain_archetype"] == "tower_domain"
    assert isinstance(record["layout_seed"], str)
    assert record["mutation_level"] == 0
    assert record["active_mutations"] == []
    assert record["playability_status"] == "UNGENERATED_VALID"
    assert len(record["identity_anchors"]) > 0 # Should load from dummy rules

def test_make_floor_record_invalid_floor_id():
    result = floor_record_builder.make_floor_record(0)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"
    result = floor_record_builder.make_floor_record("one") # type: ignore
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

def test_make_floor_record_missing_content_pack_id():
    result = floor_record_builder.make_floor_record(1, content_pack_id="")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test validate_floor_record ---
def test_validate_floor_record_success():
    record_result = floor_record_builder.make_floor_record(1)
    assert record_result["ok"] is True
    validation_result = floor_record_builder.validate_floor_record(record_result["payload"])
    assert validation_result["ok"] is True

def test_validate_floor_record_failure():
    invalid_record = floor_record_builder.make_floor_record(1)["payload"]
    invalid_record["floor_id"] = "not_an_int" # Make it invalid
    validation_result = floor_record_builder.validate_floor_record(invalid_record)
    assert validation_result["ok"] is False
    assert validation_result["error_type"] == "SchemaValidationFailure"

# --- Test make_floor_records ---
def test_make_floor_records_success():
    result = floor_record_builder.make_floor_records(count=3)
    assert result["ok"] is True
    records = result["payload"]
    assert len(records) == 3
    assert records[0]["floor_id"] == 1
    assert records[1]["floor_id"] == 2
    assert records[2]["floor_id"] == 3
    assert floor_record_builder.validate_floor_record(records[0])["ok"] is True

def test_make_floor_records_invalid_count():
    result = floor_record_builder.make_floor_records(count=0)
    assert result["ok"] is True # make_floor_records doesn't explicitly fail for count 0, returns empty list
    assert len(result["payload"]) == 0

# --- Test debug logging ---
@patch('engine.floor_generation.runtime.floor_record_builder._debug_logger_available', True)
@patch('engine.floor_generation.runtime.floor_record_builder.debug_logger.write_debug_event')
@patch('engine.floor_generation.runtime.floor_record_builder.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_floor_record_builder_debug_logging(mock_make_event, mock_write_event):
    floor_record_builder.make_floor_record(1, debug=True)
    assert mock_make_event.called
    assert mock_write_event.called

@patch('engine.floor_generation.runtime.floor_record_builder._debug_logger_available', False)
@patch('builtins.print')
def test_floor_record_builder_functional_without_debug_logger(mock_print):
    result = floor_record_builder.make_floor_record(1, debug=True)
    assert result["ok"] is True
    # Check that warning is printed when debug is true but logger unavailable
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Creating floor record for floor_id: 1")