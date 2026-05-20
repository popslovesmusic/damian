import pytest
import pytest
import os
import json
import sys
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path for module imports
PROJECT_ROOT_FOR_TESTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT_FOR_TESTS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_FOR_TESTS)

from engine.reports.runtime import mvp_end_to_end_report
from engine.core.orchestrator import mvp_startup_orchestrator
from engine.simulation.runtime import mvp_scripted_simulation
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper


REPORTS_OUTPUT_DIR = None
SIMULATIONS_SAVE_DIR = None


@pytest.fixture(autouse=True)
def setup_teardown_test_dir(tmp_path):
    """Use tmp_path for all report/simulation artifacts (no repo writes)."""
    global REPORTS_OUTPUT_DIR, SIMULATIONS_SAVE_DIR
    REPORTS_OUTPUT_DIR = str(tmp_path / "outputs" / "reports")
    SIMULATIONS_SAVE_DIR = str(tmp_path / "outputs" / "simulations")
    os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(SIMULATIONS_SAVE_DIR, exist_ok=True)
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
    with patch('engine.reports.runtime.mvp_end_to_end_report._debug_logger_available', True):
        with patch('engine.reports.runtime.mvp_end_to_end_report.debug_logger', real_debug_logger) as mock_dl:
            yield mock_dl

# --- Mock mvp_startup_orchestrator and mvp_scripted_simulation for run_mvp_end_to_end_report ---
@pytest.fixture
def mock_startup_orchestrator():
    with patch('engine.reports.runtime.mvp_end_to_end_report._mvp_components_available', True):
        with patch('engine.reports.runtime.mvp_end_to_end_report.mvp_startup_orchestrator') as mock_smo:
            mock_smo.make_default_runtime_paths.return_value = {
                "state_machine_states": "dummy_sm_states.json",
                "state_machine_transitions": "dummy_sm_transitions.json",
                "tower_state": "dummy_tower_state.json",
                "tower_state_schema": "dummy_tower_schema.json",
                "player_progression": "dummy_player_progression.json",
                "player_progression_schema": "dummy_player_schema.json",
                "domain_state": "dummy_domain_state.json",
                "domain_state_schema": "dummy_domain_schema.json",
            }
            mock_smo.startup_mvp_runtime.return_value = {
                "ok": True, "engine_version": "0.0.1", "content_pack_id": "damian",
                "state_machine": {}, "state_context": {}, "tower_state": tower_state_bootstrapper.make_default_tower_state(),
                "player_progression": {}, "domain_state": {}, "errors": [], "debug_enabled": False
            }
            yield mock_smo

@pytest.fixture
def mock_scripted_simulation():
    with patch('engine.reports.runtime.mvp_end_to_end_report.mvp_scripted_simulation') as mock_mss:
        mock_mss.make_scripted_sequence.return_value = ["VICTORY_ASCEND", "VICTORY_ASCEND", "DEFEAT_DROP", "VICTORY_ASCEND", "EXIT_GAME"]
        mock_mss.run_scripted_simulation.return_value = {
            "ok": True,
            "payload": {
                "ok": True, "sequence_name": "test_sequence", "steps_executed": 5,
                "final_floor": 3, "highest_floor_reached": 3, "mutation_events_triggered": 1,
                "residue_records_written": 5, "final_tower_state_path": "/test/path/final_tower_state.json",
                "errors": []
            }
        }
        yield mock_mss


# --- Test run_mvp_end_to_end_report ---
def test_run_mvp_end_to_end_report_success(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    # Prevent diff artifact generation from requiring a real final tower state file.
    with patch('engine.reports.runtime.mvp_end_to_end_report._replay_floor_diff_reporter_available', False):
        result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, write_to_disk=True)
    assert result["ok"] is True
    report = result["payload"]

    assert report["ok"] is True
    assert report["startup_ok"] is True
    assert report["steps_executed"] == 5
    assert report["highest_floor_reached"] == 3
    assert report["final_floor"] == 3
    assert report["residue_records_written"] == 5
    assert report["mutation_events_triggered"] == 1
    assert report["survivor_marks_attached"] == 1 # Expect one from DEFEAT_DROP
    assert report["final_tower_state_path"] == "/test/path/final_tower_state.json"
    assert not report["errors"]
    assert os.path.exists(result["path"]) # Check report artifact itself
    
    # Check scope creep flags are false
    assert report["no_scope_creep_flags"]["combat_runtime_introduced"] is False
    assert report["no_scope_creep_flags"]["map_generation_introduced"] is False

def test_run_mvp_end_to_end_report_startup_failure(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    mock_startup_orchestrator.startup_mvp_runtime.return_value = {"ok": False, "errors": [{"error_type": "StartupError", "message": "Failed"}]}
    with patch('engine.reports.runtime.mvp_end_to_end_report._replay_floor_diff_reporter_available', False):
        result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, write_to_disk=True)
    assert result["ok"] is True
    assert result["payload"]["ok"] is False
    report = result["payload"]
    assert report["startup_ok"] is False
    assert report["errors"]
    assert report["steps_executed"] == 0 # Simulation should not run
    assert os.path.exists(result["path"])

def test_run_mvp_end_to_end_report_simulation_failure(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    mock_scripted_simulation.run_scripted_simulation.return_value = {
        "ok": False,
        "error": {"error_type": "SimError", "message": "Sim failed"},
        "payload": {"ok": False, "errors": [{"error_type": "SimError", "message": "Sim failed"}]},
    }
    with patch('engine.reports.runtime.mvp_end_to_end_report._replay_floor_diff_reporter_available', False):
        result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, write_to_disk=True)
    assert result["ok"] is True
    assert result["payload"]["ok"] is False
    report = result["payload"]
    assert report["startup_ok"] is True # Startup was fine
    assert report["errors"]
    assert report["errors"][0]["error_type"] == "SimulationFailure"
    assert os.path.exists(result["path"])

# --- Test validate_mvp_report ---
def test_validate_mvp_report_success():
    mock_report = {
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-031", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True, "final_tower_state_path": "path",
        "replay_floor_diff_included": False, "replay_floor_diff_report_path": None,
        "replay_floor_diff_summary": [], "replay_floor_changed": False,
        "replay_floor_mutation_level_delta": 0, "replay_floor_new_survivor_marks": 0,
        "no_scope_creep_flags": {"combat_runtime_introduced": False, "map_generation_introduced": False, "multiplayer_runtime_introduced": False, "gpu_code_introduced": False},
        "errors": []
    }
    result = mvp_end_to_end_report.validate_mvp_report(mock_report)
    assert result["ok"] is True

def test_validate_mvp_report_missing_key():
    mock_report = {
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-031", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True,
        "replay_floor_diff_included": False, "replay_floor_diff_report_path": None,
        "replay_floor_diff_summary": [], "replay_floor_changed": False,
        "replay_floor_mutation_level_delta": 0, "replay_floor_new_survivor_marks": 0,
        "no_scope_creep_flags": {"combat_runtime_introduced": False, "map_generation_introduced": False, "multiplayer_runtime_introduced": False, "gpu_code_introduced": False},
        "errors": []
    }
    result = mvp_end_to_end_report.validate_mvp_report(mock_report)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidReportStructure"

# --- Test write_mvp_report ---
def test_write_mvp_report_success(setup_teardown_test_dir):
    mock_report = {"report": "data"}
    output_path = os.path.join(REPORTS_OUTPUT_DIR, "test_report.json")
    result = mvp_end_to_end_report.write_mvp_report(mock_report, output_path)
    assert result["ok"] is True
    assert os.path.exists(output_path)
    with open(output_path, 'r') as f:
        loaded_report = json.load(f)
    assert loaded_report == mock_report

# --- Test summarize_mvp_report ---
def test_summarize_mvp_report_success():
    mock_report = {
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-031", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True, "final_tower_state_path": "path",
        "replay_floor_diff_included": False, "replay_floor_diff_report_path": None,
        "replay_floor_diff_summary": [], "replay_floor_changed": False,
        "replay_floor_mutation_level_delta": 0, "replay_floor_new_survivor_marks": 0,
        "no_scope_creep_flags": {"combat_runtime_introduced": False, "map_generation_introduced": False, "multiplayer_runtime_introduced": False, "gpu_code_introduced": False},
        "errors": []
    }
    result = mvp_end_to_end_report.summarize_mvp_report(mock_report)
    assert result["ok"] is True
    summary = result["payload"]
    assert summary["ok"] is True
    assert summary["details"]["steps_executed"] == 5

# --- Test debug logging ---
@patch('engine.reports.runtime.mvp_end_to_end_report._debug_logger_available', True)
@patch('engine.reports.runtime.mvp_end_to_end_report.debug_logger.write_debug_event')
@patch('engine.reports.runtime.mvp_end_to_end_report.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True})
def test_report_debug_logging(
    mock_make_event, mock_write_event, mock_startup_orchestrator, mock_scripted_simulation,
    setup_teardown_test_dir
):
    mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, debug=True, write_to_disk=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("ReportStart" in c.args for c in mock_make_event.call_args_list)

@patch('engine.reports.runtime.mvp_end_to_end_report._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.reports.runtime.mvp_end_to_end_report._mvp_components_available', True)
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_startup_orchestrator')
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_scripted_simulation')
def test_report_functional_without_debug_logger(
    mock_mss, mock_smo, mock_print, setup_teardown_test_dir
):
    mock_smo.make_default_runtime_paths.return_value = {}
    mock_smo.startup_mvp_runtime.return_value = {"ok": True, "errors": []}
    mock_mss.make_scripted_sequence.return_value = ["EXIT_GAME"]
    mock_mss.run_scripted_simulation.return_value = {
        "ok": True,
        "payload": {
            "ok": True,
            "steps_executed": 1,
            "highest_floor_reached": 1,
            "final_floor": 1,
            "residue_records_written": 0,
            "mutation_events_triggered": 0,
            "final_tower_state_path": "/test/path/final_tower_state.json",
            "errors": [],
        },
    }

    result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, debug=True, write_to_disk=True)
    assert result["ok"] is True
    # debug logger is optional; warning output is configuration-dependent
