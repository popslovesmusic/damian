import pytest
import os
import json
import shutil
import sys
import datetime
import random
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.mutation.runtime import mvp_floor_mutation_stub
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper # To get a valid tower_state
from engine.residue.runtime import mvp_residue_writer # For floor memory creation

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MUTATION_EVENT_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/mutation/contracts/floor_mutation_event.schema.json")
FLOOR_MEMORY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
FLOOR_IDENTITY_RULES_PATH = os.path.join(PROJECT_ROOT, "engine/floor_generation/identity/floor_identity_preservation_rules.json")


# Define a temporary directory for tests
TEST_DIR = "test_temp_mutation_stub_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # Create dummy schema files for validation
    dummy_mutation_event_schema = {
        "type": "object",
        "properties": {
            "mutation_event_id": {"type": "string"},
            "floor_id": {"type": "integer", "minimum": 1},
            "source_outcome": {"type": "string", "enum": ["DEFEAT_DROP"]},
            "triggering_residue_id": {"type": "string"},
            "applied_channels": {"type": "array", "items": {"type": "string"}},
            "mutations": {"type": "array", "items": {
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "mutation_id": {"type": "string"},
                    "severity": {"type": "integer", "minimum": 1, "maximum": 5},
                    "preserves_floor_identity": {"type": "boolean"},
                    "preserves_playability": {"type": "boolean"}
                },
                "required": ["channel_id", "mutation_id", "severity", "preserves_floor_identity", "preserves_playability"]
            }},
            "floor_identity_preserved": {"type": "boolean"},
            "playability_preserved": {"type": "boolean"},
            "mutation_timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["mutation_event_id", "floor_id", "source_outcome", "triggering_residue_id", "applied_channels", "mutations", "floor_identity_preserved", "playability_preserved", "mutation_timestamp"]
    }
    os.makedirs(os.path.dirname(MUTATION_EVENT_SCHEMA_PATH), exist_ok=True)
    with open(MUTATION_EVENT_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_mutation_event_schema, f)

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
            "residue_history": {"type": "array", "items": {"type": "object"}} # Simplified for this schema test
        },
        "required": ["floor_id", "visit_count", "death_count", "victory_count", "stability", "deviation", "mutation_level", "known_layout_seed", "active_mutations", "discovered_easter_eggs", "unclaimed_easter_eggs", "residue_history"]
    }
    os.makedirs(os.path.dirname(FLOOR_MEMORY_SCHEMA_PATH), exist_ok=True)
    with open(FLOOR_MEMORY_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_floor_memory_schema, f)

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
    with patch('engine.mutation.runtime.mvp_floor_mutation_stub._debug_logger_available', True):
        with patch('engine.mutation.runtime.mvp_floor_mutation_stub.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Tower State ---
@pytest.fixture
def mock_tower_state():
    return tower_state_bootstrapper.make_default_tower_state()


# --- Test make_stub_mutation_event ---
def test_make_stub_mutation_event_success():
    result = mvp_floor_mutation_stub.make_stub_mutation_event(1, "residue_123")
    assert result["ok"] is True
    event = result["payload"]
    assert event["floor_id"] == 1
    assert event["source_outcome"] == "DEFEAT_DROP"
    assert event["triggering_residue_id"] == "residue_123"
    assert "layout" in event["applied_channels"]
    assert event["floor_identity_preserved"] is True
    assert event["playability_preserved"] is True
    assert isinstance(event["mutation_timestamp"], str)
    assert len(event["mutations"]) == 3 # Should contain default stub mutations

    # Validate against schema
    validation_result = json_save_manager.validate_json(event, MUTATION_EVENT_SCHEMA_PATH)
    assert validation_result["ok"] is True

def test_make_stub_mutation_event_invalid_floor_id():
    result = mvp_floor_mutation_stub.make_stub_mutation_event(0, "residue_123")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test apply_stub_mutation_to_floor_memory ---
def test_apply_stub_mutation_to_floor_memory_success(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]
    
    mutation_event = mvp_floor_mutation_stub.make_stub_mutation_event(1)["payload"]

    initial_stability = floor_memory["stability"]
    initial_deviation = floor_memory["deviation"]

    result = mvp_floor_mutation_stub.apply_stub_mutation_to_floor_memory(floor_memory, mutation_event)
    assert result["ok"] is True
    updated_fm = result["payload"]
    assert updated_fm["mutation_level"] == 1
    assert len(updated_fm["active_mutations"]) == 3 # From the stub mutations
    assert updated_fm["stability"] < initial_stability
    assert updated_fm["deviation"] > initial_deviation
    assert 0.0 <= updated_fm["stability"] <= 1.0
    assert 0.0 <= updated_fm["deviation"] <= 1.0

    # Ensure it's valid against its schema
    validation_result = json_save_manager.validate_json(updated_fm, FLOOR_MEMORY_SCHEMA_PATH)
    assert validation_result["ok"] is True

# --- Test apply_replay_floor_mutation_stub ---
def test_apply_replay_floor_mutation_stub_success(mock_tower_state):
    # Ensure floor memory exists for floor 1
    mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)

    result = mvp_floor_mutation_stub.apply_replay_floor_mutation_stub(mock_tower_state, 1, "residue_456")
    assert result["ok"] is True
    updated_tower_state = result["payload"]
    
    fm = mvp_residue_writer.get_or_create_floor_memory(updated_tower_state, 1)["payload"]
    assert fm["mutation_level"] == 1
    assert len(fm["active_mutations"]) == 3
    assert "residue_history" in fm # mvp_residue_writer creates this, but mutation stub doesn't add to it

def test_apply_replay_floor_mutation_stub_without_residue_writer_available(mock_tower_state):
    # Simulate mvp_residue_writer not being available
    with patch('engine.mutation.runtime.mvp_floor_mutation_stub.mvp_residue_writer', None):
        with patch('engine.mutation.runtime.mvp_floor_mutation_stub._log_debug_event') as mock_log:
            result = mvp_floor_mutation_stub.apply_replay_floor_mutation_stub(mock_tower_state, 1, "residue_789")
            assert result["ok"] is True
            # Should log a warning about mvp_residue_writer unavailable
            assert any("ResidueWriterUnavailable" in call[0][3] for call in mock_log.call_args_list)

# --- Test debug logging ---
@patch('engine.mutation.runtime.mvp_floor_mutation_stub._debug_logger_available', True)
@patch('engine.mutation.runtime.mvp_floor_mutation_stub.debug_logger.write_debug_event')
@patch('engine.mutation.runtime.mvp_floor_mutation_stub.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_mutation_stub_debug_logging(mock_make_event, mock_write_event, mock_tower_state):
    mvp_floor_mutation_stub.apply_replay_floor_mutation_stub(mock_tower_state, 1, "residue_test", debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("ApplyReplayMutation" in call[0][3] for call in mock_make_event.call_args_list)

@patch('engine.mutation.runtime.mvp_floor_mutation_stub._debug_logger_available', False)
@patch('builtins.print')
def test_mutation_stub_functional_without_debug_logger(mock_print, mock_tower_state):
    result = mvp_floor_mutation_stub.apply_replay_floor_mutation_stub(mock_tower_state, 1, "residue_test", debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Applying replay floor mutation stub for floor 1.")