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

from engine.simulation.runtime import mvp_scripted_simulation
from engine.save.bootstrap import tower_state_bootstrapper
from engine.player.bootstrap import player_progression_bootstrapper
from engine.domain.bootstrap import domain_state_bootstrapper
from engine.save.runtime import json_save_manager
from engine.prototype.runtime import mvp_outcome_pipeline


# Define a temporary directory for tests
TEST_DIR = "test_temp_simulation_dir"
SIMULATION_SAVE_DIR = os.path.join(TEST_DIR, "saves/simulations")

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)

    # Create dummy schemas and initial states for bootstrappers/pipeline to work
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    # State Machine Schemas
    os.makedirs(os.path.join(project_root, "engine/core/state_machine"), exist_ok=True)
    with open(os.path.join(project_root, "engine/core/state_machine/game_loop_states.json"), 'w') as f: json.dump({"states": [{"state_id": "BOOT_ENGINE"}, {"state_id": "LOAD_CONTENT_PACK"}, {"state_id": "VICTORY_ASCEND"}, {"state_id": "DEFEAT_DROP"}, {"state_id": "EXIT_GAME"}]}, f)
    with open(os.path.join(project_root, "engine/core/state_machine/game_loop_transitions.json"), 'w') as f: json.dump({"transitions": [["BOOT_ENGINE", "LOAD_CONTENT_PACK"]]}, f)

    # Tower State Schemas
    os.makedirs(os.path.join(project_root, "engine/save/schemas"), exist_ok=True)
    with open(os.path.join(project_root, "engine/save/schemas/tower_state.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "tower_state_id": {"type": "string"}, "engine_version": {"type": "string"},
                "content_pack_id": {"type": "string"}, "current_floor": {"type": "integer", "minimum": 1},
                "highest_floor_reached": {"type": "integer", "minimum": 1},
                "total_runs": {"type": "integer", "minimum": 0}, "total_deaths": {"type": "integer", "minimum": 0},
                "last_outcome": {"type": "string"}, "updated_at": {"type": "string"},
                "global_residue": {"type": "object"}, "floor_memory": {"type": "array"}
            },
            "required": ["tower_state_id", "engine_version", "content_pack_id", "current_floor", "highest_floor_reached", "total_runs", "total_deaths", "last_outcome", "updated_at", "global_residue", "floor_memory"]
        }, f)
    with open(os.path.join(project_root, "engine/save/schemas/floor_memory.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "floor_id": {"type": "integer", "minimum": 1}, "visit_count": {"type": "integer"}, "death_count": {"type": "integer"}, "victory_count": {"type": "integer"},
                "stability": {"type": "number"}, "deviation": {"type": "number"}, "mutation_level": {"type": "integer"},
                "known_layout_seed": {"type": "string"}, "active_mutations": {"type": "array"}, "discovered_easter_eggs": {"type": "array"},
                "unclaimed_easter_eggs": {"type": "array"}, "residue_history": {"type": "array"}
            },
            "required": ["floor_id", "visit_count", "death_count", "victory_count", "stability", "deviation", "mutation_level", "known_layout_seed", "active_mutations", "discovered_easter_eggs", "unclaimed_easter_eggs", "residue_history"]
        }, f)
    with open(os.path.join(project_root, "engine/save/schemas/residue_record.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "residue_id": {"type": "string"}, "floor_id": {"type": "integer"}, "outcome": {"type": "string"},
                "dominant_damage_type": {"type": "string"}, "most_used_skill": {"type": "string"},
                "clear_time_seconds": {"type": "number"}, "exploration_percent": {"type": "number"},
                "party_size": {"type": "integer"}, "death_event": {"type": "boolean"},
                "mutation_triggered": {"type": "boolean"}, "notes": {"type": "array"}
            },
            "required": ["residue_id", "floor_id", "outcome", "dominant_damage_type", "most_used_skill", "clear_time_seconds", "exploration_percent", "party_size", "death_event", "mutation_triggered", "notes"]
        }, f)

    # Player Progression Schemas
    os.makedirs(os.path.join(project_root, "engine/player/contracts"), exist_ok=True)
    with open(os.path.join(project_root, "engine/player/contracts/player_progression_state.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "player_id": {"type": "string"}, "profile_id": {"type": "string"},
                "content_pack_id": {"type": "string"}, "level": {"type": "integer"},
                "highest_floor_reached": {"type": "integer"}, "active_orientation": {"type": "string"},
                "stats": {"type": "object"}, "unlocked_skills": {"type": "array"},
                "equipped_items": {"type": "array"}, "residue_pressure": {"type": "object"},
                "forbidden_flags": {"type": "object"}
            },
            "required": ["player_id", "profile_id", "content_pack_id", "level", "highest_floor_reached", "active_orientation", "stats", "unlocked_skills", "equipped_items", "residue_pressure", "forbidden_flags"]
        }, f)
    
    # Domain State Schemas
    os.makedirs(os.path.join(project_root, "engine/domain/contracts"), exist_ok=True)
    with open(os.path.join(project_root, "engine/domain/contracts/domain_state.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "domain_state_id": {"type": "string"}, "owner_player_id": {"type": "string"},
                "content_pack_id": {"type": "string"}, "domain_archetype": {"type": "string"},
                "conquered": {"type": "boolean"}, "dashboard_unlocked": {"type": "boolean"},
                "domain_level": {"type": "integer"}, "stability": {"type": "number"},
                "deviation": {"type": "number"}, "active_modifiers": {"type": "array"},
                "operational_costs": {"type": "object"}, "invasion_history": {"type": "array"},
                "forbidden_flags": {"type": "object"}
            },
            "required": ["domain_state_id", "owner_player_id", "content_pack_id", "domain_archetype", "conquered", "dashboard_unlocked", "domain_level", "stability", "deviation", "active_modifiers", "operational_costs", "invasion_history", "forbidden_flags"]
        }, f)

    # Mutation event schema (needed by mvp_floor_mutation_stub)
    os.makedirs(os.path.join(project_root, "engine/mutation/contracts"), exist_ok=True)
    with open(os.path.join(project_root, "engine/mutation/contracts/floor_mutation_event.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "mutation_event_id": {"type": "string"}, "floor_id": {"type": "integer"},
                "source_outcome": {"type": "string"}, "triggering_residue_id": {"type": "string"},
                "applied_channels": {"type": "array"}, "mutations": {"type": "array"},
                "floor_identity_preserved": {"type": "boolean"}, "playability_preserved": {"type": "boolean"},
                "mutation_timestamp": {"type": "string"}
            },
            "required": ["mutation_event_id", "floor_id", "source_outcome", "triggering_residue_id", "applied_channels", "mutations", "floor_identity_preserved", "playability_preserved", "mutation_timestamp"]
        }, f)

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
    with patch('engine.simulation.runtime.mvp_scripted_simulation._debug_logger_available', True):
        with patch('engine.simulation.runtime.mvp_scripted_simulation.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Test make_scripted_sequence ---
def test_make_scripted_sequence_default():
    sequence = mvp_scripted_simulation.make_scripted_sequence()
    assert len(sequence) == 5
    assert sequence == ["VICTORY_ASCEND", "VICTORY_ASCEND", "DEFEAT_DROP", "VICTORY_ASCEND", "EXIT_GAME"]

# --- Test run_scripted_simulation ---
@patch('engine.simulation.runtime.mvp_scripted_simulation._mvp_outcome_pipeline_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._bootstrappers_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._json_save_manager_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.bootstrap_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.player_progression_bootstrapper.bootstrap_player_progression')
@patch('engine.simulation.runtime.mvp_scripted_simulation.domain_state_bootstrapper.bootstrap_domain_state')
@patch('engine.simulation.runtime.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.save_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.json_save_manager.save_json')
def test_run_scripted_simulation_success(
    mock_save_json, mock_save_tower_state, mock_resolve_outcome,
    mock_bootstrap_domain, mock_bootstrap_player, mock_bootstrap_tower,
    setup_teardown_test_dir
):
    # Setup mocks for successful bootstrapping
    mock_bootstrap_tower.return_value = {"ok": True, "payload": {"current_floor": 1, "highest_floor_reached": 1, "floor_memory": [], "global_residue": {}}}
    mock_bootstrap_player.return_value = {"ok": True, "payload": {}}
    mock_bootstrap_domain.return_value = {"ok": True, "payload": {}}

    # Setup mocks for pipeline resolution
    # Sequence: VICTORY_ASCEND, VICTORY_ASCEND, DEFEAT_DROP, VICTORY_ASCEND, EXIT_GAME
    mock_resolve_outcome.side_effect = [
        {"ok": True, "tower_state": {"current_floor": 2, "highest_floor_reached": 2, "floor_memory": [{"floor_id":1, "visit_count":1, "victory_count":1}]}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False},
        {"ok": True, "tower_state": {"current_floor": 3, "highest_floor_reached": 3, "floor_memory": [{"floor_id":1, "visit_count":1, "victory_count":1}, {"floor_id":2, "visit_count":1, "victory_count":1}]}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False},
        {"ok": True, "tower_state": {"current_floor": 2, "highest_floor_reached": 3, "floor_memory": [{"floor_id":1, "visit_count":1, "victory_count":1}, {"floor_id":2, "visit_count":2, "death_count":1, "mutation_level":1, "active_mutations":["mvp_defeat_mutation"], "residue_history":[]}]}, "residue_result": {"ok": True, "payload": {"residue_record": {"residue_id": "sim_res_1"}}}, "mutation_applied": True, "mutation_result": {"ok": True, "payload": {"mutation_event":{}}}, "shutdown_requested": False},
        {"ok": True, "tower_state": {"current_floor": 3, "highest_floor_reached": 3, "floor_memory": [{"floor_id":1, "visit_count":1, "victory_count":1}, {"floor_id":2, "visit_count":2, "death_count":1, "mutation_level":1, "active_mutations":["mvp_defeat_mutation"], "residue_history":[]}, {"floor_id":3, "visit_count":1, "victory_count":1}]}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False},
        {"ok": True, "tower_state": {"current_floor": 3, "highest_floor_reached": 3}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": True}
    ]
    mock_save_tower_state.return_value = {"ok": True}
    mock_save_json.return_value = {"ok": True} # For simulation result artifact

    sequence = mvp_scripted_simulation.make_scripted_sequence()
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR)

    assert result["ok"] is True
    summary = result["payload"]
    assert summary["steps_executed"] == 5
    assert summary["final_floor"] == 3
    assert summary["highest_floor_reached"] == 3
    assert summary["mutation_events_triggered"] == 1
    assert summary["residue_records_written"] == 5
    assert "sim_" in summary["final_tower_state_path"]
    assert not summary["errors"]
    
    # Check that save_tower_state was called with the final tower state
    assert mock_save_tower_state.called
    final_tower_state_arg = mock_save_tower_state.call_args[0][1] # Second arg is tower_state
    assert final_tower_state_arg["current_floor"] == 3
    assert final_tower_state_arg["highest_floor_reached"] == 3
    
    # Check for mutation persistence (floor 2 should show mutation from DEFEAT_DROP)
    floor2_memory = next((f for f in final_tower_state_arg["floor_memory"] if f["floor_id"] == 2), None)
    assert floor2_memory is not None
    assert floor2_memory["mutation_level"] == 1
    assert "mvp_defeat_mutation" in floor2_memory["active_mutations"]


@patch('engine.simulation.runtime.mvp_scripted_simulation._mvp_outcome_pipeline_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._bootstrappers_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._json_save_manager_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.bootstrap_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.player_progression_bootstrapper.bootstrap_player_progression')
@patch('engine.simulation.runtime.mvp_scripted_simulation.domain_state_bootstrapper.bootstrap_domain_state')
@patch('engine.simulation.runtime.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.save_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.json_save_manager.save_json')
def test_run_scripted_simulation_pipeline_failure(
    mock_save_json, mock_save_tower_state, mock_resolve_outcome,
    mock_bootstrap_domain, mock_bootstrap_player, mock_bootstrap_tower,
    setup_teardown_test_dir
):
    mock_bootstrap_tower.return_value = {"ok": True, "payload": {"current_floor": 1, "highest_floor_reached": 1}}
    mock_bootstrap_player.return_value = {"ok": True, "payload": {}}
    mock_bootstrap_domain.return_value = {"ok": True, "payload": {}}

    # Simulate a pipeline failure on the second step
    mock_resolve_outcome.side_effect = [
        {"ok": True, "tower_state": {"current_floor": 2, "highest_floor_reached": 2}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False},
        {"ok": False, "error": {"error_type": "ProgressionFailure", "message": "Simulated error"}}, # Fail here
        {"ok": True, "tower_state": {"current_floor": 1, "highest_floor_reached": 2}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": True, "shutdown_requested": False} # This won't be reached
    ]
    mock_save_tower_state.return_value = {"ok": True}
    mock_save_json.return_value = {"ok": True}

    sequence = mvp_scripted_simulation.make_scripted_sequence()
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR)

    assert result["ok"] is False
    summary = result["payload"]
    assert summary["steps_executed"] == 1 # Only one successful step before failure
    assert len(summary["errors"]) == 1
    assert summary["errors"][0]["error_type"] == "ProgressionFailure"

def test_summarize_simulation_result():
    mock_sim_result = {
        "ok": True,
        "sequence_name": "test_seq",
        "steps_executed": 5,
        "final_floor": 3,
        "highest_floor_reached": 3,
        "mutation_events_triggered": 1,
        "residue_records_written": 5,
        "final_tower_state_path": "/path/to/save",
        "errors": []
    }
    summary = mvp_scripted_simulation.summarize_simulation_result(mock_sim_result)["payload"]
    assert summary["ok"] is True
    assert summary["steps_executed"] == 5

def test_load_simulation_results_success(setup_teardown_test_dir):
    sim_output_dir = os.path.join(SIMULATION_SAVE_DIR, "test_sim_id")
    os.makedirs(sim_output_dir)
    test_result_path = os.path.join(sim_output_dir, "test_sim_id_result.json")
    test_data = {"key": "value"}
    json_save_manager.save_json(test_result_path, test_data)

    result = mvp_scripted_simulation.load_simulation_results(test_result_path)
    assert result["ok"] is True
    assert result["payload"] == test_data

def test_load_simulation_results_not_found():
    result = mvp_scripted_simulation.load_simulation_results("non_existent.json")
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"

# --- Test debug logging ---
@patch('engine.simulation.runtime.mvp_scripted_simulation._debug_logger_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation.debug_logger.write_debug_event')
@patch('engine.simulation.runtime.mvp_scripted_simulation.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True, "args": args, "kwargs": kwargs})
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.bootstrap_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.player_progression_bootstrapper.bootstrap_player_progression')
@patch('engine.simulation.runtime.mvp_scripted_simulation.domain_state_bootstrapper.bootstrap_domain_state')
@patch('engine.simulation.runtime.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.save_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.json_save_manager.save_json')
def test_simulation_debug_logging(
    mock_save_json, mock_save_tower_state, mock_resolve_outcome,
    mock_bootstrap_domain, mock_bootstrap_player, mock_bootstrap_tower,
    mock_make_event, mock_write_event, setup_teardown_test_dir
):
    mock_bootstrap_tower.return_value = {"ok": True, "payload": {"current_floor": 1, "highest_floor_reached": 1, "floor_memory": [], "global_residue": {}}}
    mock_bootstrap_player.return_value = {"ok": True, "payload": {}}
    mock_bootstrap_domain.return_value = {"ok": True, "payload": {}}
    mock_resolve_outcome.return_value = {"ok": True, "tower_state": {"current_floor": 2, "highest_floor_reached": 2}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False}
    mock_save_tower_state.return_value = {"ok": True}
    mock_save_json.return_value = {"ok": True}

    sequence = ["VICTORY_ASCEND"] # A short sequence for testing
    mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("SimulationStart" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.simulation.runtime.mvp_scripted_simulation._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.simulation.runtime.mvp_scripted_simulation._mvp_outcome_pipeline_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._bootstrappers_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._json_save_manager_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.bootstrap_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.player_progression_bootstrapper.bootstrap_player_progression')
@patch('engine.simulation.runtime.mvp_scripted_simulation.domain_state_bootstrapper.bootstrap_domain_state')
@patch('engine.simulation.runtime.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.save_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.json_save_manager.save_json')
def test_simulation_functional_without_debug_logger(
    mock_save_json, mock_save_tower_state, mock_resolve_outcome,
    mock_bootstrap_domain, mock_bootstrap_player, mock_bootstrap_tower,
    mock_print, setup_teardown_test_dir
):
    mock_bootstrap_tower.return_value = {"ok": True, "payload": {"current_floor": 1, "highest_floor_reached": 1, "floor_memory": [], "global_residue": {}}}
    mock_bootstrap_player.return_value = {"ok": True, "payload": {}}
    mock_bootstrap_domain.return_value = {"ok": True, "payload": {}}
    mock_resolve_outcome.return_value = {"ok": True, "tower_state": {"current_floor": 2, "highest_floor_reached": 2}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": False}
    mock_save_tower_state.return_value = {"ok": True}
    mock_save_json.return_value = {"ok": True}

    sequence = ["VICTORY_ASCEND"]
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Starting scripted simulation.")