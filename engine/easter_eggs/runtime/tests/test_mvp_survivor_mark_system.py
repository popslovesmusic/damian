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

from engine.easter_eggs.runtime import mvp_survivor_mark_system
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper # To get a valid tower_state
from engine.residue.runtime import mvp_residue_writer # For floor memory creation

# Paths to existing schemas and example data from previous patches (relative to project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SURVIVOR_MARK_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/easter_eggs/contracts/survivor_mark.schema.json")
FLOOR_MEMORY_SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")
SURVIVOR_MARK_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "engine/easter_eggs/registry/survivor_mark_registry.json")


# Define a temporary directory for tests
TEST_DIR = "test_temp_survivor_mark_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # Create dummy survivor mark schema
    dummy_survivor_mark_schema = {
        "type": "object",
        "properties": {
            "survivor_mark_id": {"type": "string"},
            "floor_id": {"type": "integer", "minimum": 1},
            "source_mutation_event_id": {"type": "string"},
            "mark_class_id": {"type": "string"},
            "hint_modes": {"type": "array", "minItems": 1},
            "placement_context": {"type": "string"},
            "claim_condition": {"type": "string"},
            "reward_class_id": {"type": "string"},
            "reward_payload_ref": {"type": "string"},
            "is_optional": {"type": "boolean"},
            "is_discoverable": {"type": "boolean"},
            "claimed": {"type": "boolean"},
            "can_mutate_if_unclaimed": {"type": "boolean"},
            "progression_break_risk": {"type": "string", "enum": ["NONE", "LOW", "INVALID"]}
        },
        "required": ["survivor_mark_id", "floor_id", "source_mutation_event_id", "mark_class_id", "hint_modes", "placement_context", "claim_condition", "reward_class_id", "reward_payload_ref", "is_optional", "is_discoverable", "claimed", "can_mutate_if_unclaimed", "progression_break_risk"]
    }
    os.makedirs(os.path.dirname(SURVIVOR_MARK_SCHEMA_PATH), exist_ok=True)
    with open(SURVIVOR_MARK_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_survivor_mark_schema, f)

    # Create dummy floor memory schema (simplified to allow residue_history to be array of objects)
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
            "residue_history": {"type": "array"} # Simple array to pass schema, content checked by other tests
        },
        "required": ["floor_id", "visit_count", "death_count", "victory_count", "stability", "deviation", "mutation_level", "known_layout_seed", "active_mutations", "discovered_easter_eggs", "unclaimed_easter_eggs", "residue_history"]
    }
    os.makedirs(os.path.dirname(FLOOR_MEMORY_SCHEMA_PATH), exist_ok=True)
    with open(FLOOR_MEMORY_SCHEMA_PATH, 'w') as f:
        json.dump(dummy_floor_memory_schema, f)

    # Create dummy survivor mark registry
    dummy_registry = {
        "mark_classes": [
            {"mark_class_id": "visual_glyph", "discoverability_modes": ["visual_hint", "lighting_reveal"]},
            {"mark_class_id": "audio_echo", "discoverability_modes": ["proximity_audio"]}
        ],
        "reward_classes": [
            {"reward_class_id": "minor_cache"},
            {"reward_class_id": "rare_cache"},
            {"reward_class_id": "memory_fragment"},
            {"reward_class_id": "orientation_upgrade"},
            {"reward_class_id": "hidden_event_trigger"}
        ]
    }
    os.makedirs(os.path.dirname(SURVIVOR_MARK_REGISTRY_PATH), exist_ok=True)
    with open(SURVIVOR_MARK_REGISTRY_PATH, 'w') as f:
        json.dump(dummy_registry, f)

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
    with patch('engine.easter_eggs.runtime.mvp_survivor_mark_system._debug_logger_available', True):
        with patch('engine.easter_eggs.runtime.mvp_survivor_mark_system.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock Tower State ---
@pytest.fixture
def mock_tower_state():
    return tower_state_bootstrapper.make_default_tower_state()


# --- Test make_survivor_mark ---
def test_make_survivor_mark_success():
    result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert result["ok"] is True
    mark = result["payload"]
    assert mark["floor_id"] == 1
    assert mark["source_mutation_event_id"] == "mutation_001"
    assert mark["is_optional"] is True
    assert mark["is_discoverable"] is True
    assert len(mark["hint_modes"]) > 0
    assert mark["claimed"] is False
    assert mark["progression_break_risk"] == "LOW"

    # Validate against schema
    validation_result = json_save_manager.validate_json(mark, SURVIVOR_MARK_SCHEMA_PATH)
    assert validation_result["ok"] is True

def test_make_survivor_mark_invalid_floor_id():
    result = mvp_survivor_mark_system.make_survivor_mark(0, "mutation_001")
    assert result["ok"] is False
    assert result["error_type"] == "InvalidInput"

# --- Test attach_survivor_mark_to_floor_memory ---
def test_attach_survivor_mark_to_floor_memory_success(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]

    mark_result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert mark_result["ok"]
    mark = mark_result["payload"]

    result = mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark)
    assert result["ok"] is True
    assert mark["survivor_mark_id"] in floor_memory["unclaimed_easter_eggs"]

def test_attach_survivor_mark_to_floor_memory_duplicate(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]

    mark_result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert mark_result["ok"]
    mark = mark_result["payload"]

    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark) # Attach once
    result = mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark) # Attach again
    assert result["ok"] is True # Should still be ok, just not add duplicate
    assert floor_memory["unclaimed_easter_eggs"].count(mark["survivor_mark_id"]) == 1

# --- Test discover_survivor_mark ---
def test_discover_survivor_mark_success(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]
    mark_result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert mark_result["ok"]
    mark = mark_result["payload"]
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark)

    result = mvp_survivor_mark_system.discover_survivor_mark(floor_memory, mark["survivor_mark_id"])
    assert result["ok"] is True
    assert mark["survivor_mark_id"] not in floor_memory["unclaimed_easter_eggs"]
    assert mark["survivor_mark_id"] in floor_memory["discovered_easter_eggs"]

def test_discover_survivor_mark_not_found(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]

    result = mvp_survivor_mark_system.discover_survivor_mark(floor_memory, "non_existent_mark")
    assert result["ok"] is False
    assert result["error_type"] == "MarkNotFound"

# --- Test claim_survivor_mark ---
def test_claim_survivor_mark_success(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]
    mark_result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert mark_result["ok"]
    mark = mark_result["payload"]
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark)
    mvp_survivor_mark_system.discover_survivor_mark(floor_memory, mark["survivor_mark_id"])

    result = mvp_survivor_mark_system.claim_survivor_mark(floor_memory, mark["survivor_mark_id"])
    assert result["ok"] is True
    assert mark["survivor_mark_id"] not in floor_memory["discovered_easter_eggs"]
    assert "reward_id" in result["payload"]
    assert result["payload"]["type"] == "rare_cache"
    assert 500 <= result["payload"]["value"] <= 1500

def test_claim_survivor_mark_not_discovered(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]
    mark_result = mvp_survivor_mark_system.make_survivor_mark(1, "mutation_001")
    assert mark_result["ok"]
    mark = mark_result["payload"]
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark) # Only attached, not discovered

    result = mvp_survivor_mark_system.claim_survivor_mark(floor_memory, mark["survivor_mark_id"])
    assert result["ok"] is False
    assert result["error_type"] == "MarkNotDiscovered"

# --- Test list_unclaimed_survivor_marks ---
def test_list_unclaimed_survivor_marks(mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    assert floor_memory_result["ok"]
    floor_memory = floor_memory_result["payload"]

    mark1 = mvp_survivor_mark_system.make_survivor_mark(1, "m1")["payload"]
    mark2 = mvp_survivor_mark_system.make_survivor_mark(1, "m2")["payload"]
    
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark1)
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark2)
    
    # Discover one but don't claim
    mvp_survivor_mark_system.discover_survivor_mark(floor_memory, mark1["survivor_mark_id"])

    result = mvp_survivor_mark_system.list_unclaimed_survivor_marks(floor_memory)
    assert result["ok"] is True
    assert len(result["payload"]) == 1
    assert mark2["survivor_mark_id"] in result["payload"]
    assert mark1["survivor_mark_id"] not in result["payload"]

# --- Test debug logging ---
@patch('engine.easter_eggs.runtime.mvp_survivor_mark_system._debug_logger_available', True)
@patch('engine.easter_eggs.runtime.mvp_survivor_mark_system.debug_logger.write_debug_event')
@patch('engine.easter_eggs.runtime.mvp_survivor_mark_system.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
def test_system_debug_logging(mock_make_event, mock_write_event, mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    floor_memory = floor_memory_result["payload"]
    mark = mvp_survivor_mark_system.make_survivor_mark(1, "m1")["payload"]
    
    mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark, debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("AttachSurvivorMark" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.easter_eggs.runtime.mvp_survivor_mark_system._debug_logger_available', False)
@patch('builtins.print')
def test_system_functional_without_debug_logger(mock_print, mock_tower_state):
    floor_memory_result = mvp_residue_writer.get_or_create_floor_memory(mock_tower_state, 1)
    floor_memory = floor_memory_result["payload"]
    mark = mvp_survivor_mark_system.make_survivor_mark(1, "m1")["payload"]
    
    result = mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory(floor_memory, mark, debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Attaching mark {} to floor 1.".format(mark["survivor_mark_id"]))