import pytest
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


SIMULATION_SAVE_DIR = None


@pytest.fixture(autouse=True)
def setup_teardown_test_dir(tmp_path):
    """Use tmp_path for all simulation artifacts (no repo writes)."""
    global SIMULATION_SAVE_DIR
    SIMULATION_SAVE_DIR = str(tmp_path / "saves" / "simulations")
    os.makedirs(SIMULATION_SAVE_DIR, exist_ok=True)
    yield


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
@patch('engine.simulation.runtime.mvp_scripted_simulation.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
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
            {"ok": True, "tower_state": {"current_floor": 3, "highest_floor_reached": 3, "floor_memory": [{"floor_id":1, "visit_count":1, "victory_count":1}, {"floor_id":2, "visit_count":2, "death_count":1, "mutation_level":1, "active_mutations":["mvp_defeat_mutation"], "residue_history":[]}, {"floor_id":3, "visit_count":1, "victory_count":1}]}, "residue_result": {"ok": True, "payload": {"residue_record": {}}}, "mutation_applied": False, "shutdown_requested": True}
        ]
    mock_save_tower_state.return_value = {"ok": True}
    mock_save_json.return_value = {"ok": True} # For simulation result artifact

    sequence = mvp_scripted_simulation.make_scripted_sequence()
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, write_to_disk=True)

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
@patch('engine.simulation.runtime.mvp_scripted_simulation.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
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
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, write_to_disk=True)

    assert result["ok"] is True
    summary = result["payload"]
    assert summary["ok"] is False
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
@patch('engine.simulation.runtime.mvp_scripted_simulation.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
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
    mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, debug=True, write_to_disk=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("SimulationStart" in c.args for c in mock_make_event.call_args_list)

@patch('engine.simulation.runtime.mvp_scripted_simulation._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.simulation.runtime.mvp_scripted_simulation._mvp_outcome_pipeline_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._bootstrappers_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation._json_save_manager_available', True)
@patch('engine.simulation.runtime.mvp_scripted_simulation.tower_state_bootstrapper.bootstrap_tower_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.player_progression_bootstrapper.bootstrap_player_progression')
@patch('engine.simulation.runtime.mvp_scripted_simulation.domain_state_bootstrapper.bootstrap_domain_state')
@patch('engine.simulation.runtime.mvp_scripted_simulation.mvp_outcome_pipeline.resolve_mvp_floor_outcome')
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
    result = mvp_scripted_simulation.run_scripted_simulation(sequence, save_dir=SIMULATION_SAVE_DIR, debug=True, write_to_disk=True)
    assert result["ok"] is True
    # debug logger is intentionally optional; a warning may be printed in some configurations
