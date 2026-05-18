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

from engine.reports.runtime import mvp_end_to_end_report
from engine.core.orchestrator import mvp_startup_orchestrator
from engine.simulation.runtime import mvp_scripted_simulation
from engine.save.runtime import json_save_manager # For schema mocking
from engine.save.bootstrap import tower_state_bootstrapper # For default tower state
from engine.reports.runtime import replay_floor_diff_reporter # For mocking

# Define a temporary directory for tests
TEST_DIR = "test_temp_report_floor_diff_dir"
REPORTS_OUTPUT_DIR = os.path.join(TEST_DIR, "outputs/reports")
SIMULATIONS_SAVE_DIR = os.path.join(TEST_DIR, "outputs/simulations") # Simulation needs this

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(REPORTS_OUTPUT_DIR)
    os.makedirs(SIMULATIONS_SAVE_DIR) # Make sure sim output dir exists

    # Mock necessary schemas for bootstrappers/pipeline/sim to function
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
    
    # Floor identity rules (needed by mvp_floor_mutation_stub)
    os.makedirs(os.path.join(project_root, "engine/floor_generation/identity"), exist_ok=True)
    with open(os.path.join(project_root, "engine/floor/generation/identity/floor_identity_preservation_rules.json"), 'w') as f:
        json.dump({"required_identity_anchors": []}, f)

    # Survivor Mark Schema & Registry
    os.makedirs(os.path.join(project_root, "engine/easter_eggs/contracts"), exist_ok=True)
    with open(os.path.join(project_root, "engine/easter_eggs/contracts/survivor_mark.schema.json"), 'w') as f:
        json.dump({
            "type": "object",
            "properties": {
                "survivor_mark_id": {"type": "string"}, "floor_id": {"type": "integer", "minimum": 1},
                "source_mutation_event_id": {"type": "string"}, "mark_class_id": {"type": "string"},
                "hint_modes": {"type": "array", "minItems": 1}, "placement_context": {"type": "string"},
                "claim_condition": {"type": "string"}, "reward_class_id": {"type": "string"},
                "reward_payload_ref": {"type": "string"}, "is_optional": {"type": "boolean"},
                "is_discoverable": {"type": "boolean"}, "claimed": {"type": "boolean"},
                "can_mutate_if_unclaimed": {"type": "boolean"}, "progression_break_risk": {"type": "string"}
            },
            "required": ["survivor_mark_id", "floor_id", "source_mutation_event_id", "mark_class_id", "hint_modes", "placement_context", "claim_condition", "reward_class_id", "reward_payload_ref", "is_optional", "is_discoverable", "claimed", "can_mutate_if_unclaimed", "progression_break_risk"]
        }, f)
    
    os.makedirs(os.path.join(project_root, "engine/easter_eggs/registry"), exist_ok=True)
    with open(os.path.join(project_root, "engine/easter_eggs/registry/survivor_mark_registry.json"), 'w') as f:
        json.dump({
            "mark_classes": [
                {"mark_class_id": "visual_glyph", "discoverability_modes": ["visual_hint"]}
            ],
            "reward_classes": [
                {"reward_class_id": "rare_cache"}
            ]
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
                "residue_records_written": 5, "final_tower_state_path": os.path.join(SIMULATIONS_SAVE_DIR, "sim_mock_id", "final_tower_state.json"),
                "errors": []
            }
        }
        yield mock_mss


# --- Test run_mvp_end_to_end_report ---
def test_run_mvp_end_to_end_report_success(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    # Mock json_save_manager.load_json to provide the final tower state from simulation
    mock_final_tower_state = tower_state_bootstrapper.make_default_tower_state()
    mock_final_tower_state["current_floor"] = 3
    mock_final_tower_state["highest_floor_reached"] = 3
    # Simulate mutation on floor 2
    mock_final_tower_state["floor_memory"].append({
        "floor_id": 2, "visit_count": 2, "death_count": 1, "victory_count": 1,
        "stability": 0.75, "deviation": 0.15, "mutation_level": 1,
        "known_layout_seed": "mock_seed_floor_2", "active_mutations": ["mvp_defeat_mutation"],
        "discovered_easter_eggs": [], "unclaimed_easter_eggs": ["mark_new"], "residue_history": [{"id": "res1"}]
    })

    with patch('engine.reports.runtime.mvp_end_to_end_report._replay_floor_diff_reporter_available', True):
        with patch('engine.reports.runtime.mvp_end_to_end_report.json_save_manager.load_json', return_value={"ok": True, "payload": mock_final_tower_state}):
            with patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.make_replay_floor_diff_report') as mock_make_diff_report:
                mock_make_diff_report.return_value = {
                    "ok": True,
                    "payload": {
                        "report_id": "diff_report_mock", "floor_id": 2, "changed": True,
                        "before": {}, "after": {}, "changes": {"mutation_level_delta": 1, "new_unclaimed_survivor_marks": ["mark_new"]},
                        "readable_summary": ["Mutation level increased by 1.", "New unclaimed survivor marks detected: mark_new."],
                        "error": None
                    }
                }
                with patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.write_replay_floor_diff_report', return_value={"ok": True, "path": "/mock/path/diff_report.json"}):
                    result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR)
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
                    assert report["final_tower_state_path"] == os.path.join(SIMULATIONS_SAVE_DIR, "sim_mock_id", "final_tower_state.json")
                    assert not report["errors"]
                    assert os.path.exists(result["path"]) # Check report artifact itself
                    
                    # New floor diff fields
                    assert report["replay_floor_diff_included"] is True
                    assert report["replay_floor_changed"] is True
                    assert report["replay_floor_mutation_level_delta"] == 1
                    assert report["replay_floor_new_survivor_marks"] == 1
                    assert "Mutation level increased by 1." in report["replay_floor_diff_summary"]
                    
                    # Check scope creep flags are false
                    assert report["no_scope_creep_flags"]["combat_runtime_introduced"] is False
                    assert report["no_scope_creep_flags"]["map_generation_introduced"] is False

def test_run_mvp_end_to_end_report_startup_failure(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    mock_startup_orchestrator.startup_mvp_runtime.return_value = {"ok": False, "errors": [{"error_type": "StartupError", "message": "Failed"}]}
    result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR)
    assert result["ok"] is False
    report = result["payload"]
    assert report["startup_ok"] is False
    assert report["errors"]
    assert report["steps_executed"] == 0 # Simulation should not run
    assert os.path.exists(result["path"])

def test_run_mvp_end_to_end_report_simulation_failure(
    mock_startup_orchestrator, mock_scripted_simulation, setup_teardown_test_dir
):
    mock_scripted_simulation.run_scripted_simulation.return_value = {
        "ok": False, "payload": {"errors": [{"error_type": "SimError", "message": "Sim failed"}], "ok": False}
    }
    result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR)
    assert result["ok"] is False
    report = result["payload"]
    assert report["startup_ok"] is True # Startup was fine
    assert report["errors"]
    assert report["errors"][0]["error_type"] == "SimulationFailure"
    assert os.path.exists(result["path"])

# --- Test validate_mvp_report ---
def test_validate_mvp_report_success():
    mock_report = {
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-033", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True, "final_tower_state_path": "path",
        "replay_floor_diff_included": True, "replay_floor_diff_report_path": "diff_path",
        "replay_floor_diff_summary": ["summary line"], "replay_floor_changed": True,
        "replay_floor_mutation_level_delta": 1, "replay_floor_new_survivor_marks": 1,
        "no_scope_creep_flags": {"combat_runtime_introduced": False, "map_generation_introduced": False, "multiplayer_runtime_introduced": False, "gpu_code_introduced": False},
        "errors": []
    }
    result = mvp_end_to_end_report.validate_mvp_report(mock_report)
    assert result["ok"] is True

def test_validate_mvp_report_missing_key():
    mock_report = {
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-033", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True, "final_tower_state_path": "path",
        "replay_floor_diff_included": True, "replay_floor_diff_report_path": "diff_path",
        "replay_floor_diff_summary": ["summary line"], "replay_floor_changed": True,
        "replay_floor_mutation_level_delta": 1, # "replay_floor_new_survivor_marks" is missing
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
        "report_id": "test_id", "patch_id": "TOWER-ENGINE-033", "ok": True, "sequence": [],
        "startup_ok": True, "steps_executed": 5, "highest_floor_reached": 3, "final_floor": 3,
        "residue_records_written": 5, "mutation_events_triggered": 1, "survivor_marks_attached": 1,
        "survivor_marks_unclaimed": 0, "tower_state_saved": True, "final_tower_state_path": "path",
        "replay_floor_diff_included": True, "replay_floor_diff_report_path": "diff_path",
        "replay_floor_diff_summary": ["summary line"], "replay_floor_changed": True,
        "replay_floor_mutation_level_delta": 1, "replay_floor_new_survivor_marks": 1,
        "no_scope_creep_flags": {"combat_runtime_introduced": False, "map_generation_introduced": False, "multiplayer_runtime_introduced": False, "gpu_code_introduced": False},
        "errors": []
    }
    result = mvp_end_to_end_report.summarize_mvp_report(mock_report)
    assert result["ok"] is True
    summary = result["payload"]
    assert summary["ok"] is True
    assert summary["details"]["steps_executed"] == 5
    assert summary["details"]["replay_floor_diff_included"] is True
    assert summary["details"]["replay_floor_changed"] is True

# --- Test debug logging ---
@patch('engine.reports.runtime.mvp_end_to_end_report._debug_logger_available', True)
@patch('engine.reports.runtime.mvp_end_to_end_report.debug_logger.write_debug_event')
@patch('engine.reports.runtime.mvp_end_to_end_report.debug_logger.make_debug_event', side_effect=lambda *args, **kwargs: {"mock_event": True})
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_startup_orchestrator.startup_mvp_runtime')
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_scripted_simulation.run_scripted_simulation')
@patch('engine.reports.runtime.mvp_end_to_end_report.json_save_manager.load_json')
@patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.make_replay_floor_diff_report')
@patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.write_replay_floor_diff_report')
def test_report_debug_logging(
    mock_write_diff_report, mock_make_diff_report, mock_load_json,
    mock_run_simulation, mock_startup_runtime, mock_make_event, mock_write_event,
    setup_teardown_test_dir
):
    mock_startup_runtime.return_value = {"ok": True, "errors": [], "tower_state": tower_state_bootstrapper.make_default_tower_state()}
    mock_run_simulation.return_value = {
        "ok": True, "payload": {
            "ok": True, "steps_executed": 1, "errors": [],
            "final_tower_state_path": os.path.join(SIMULATIONS_SAVE_DIR, "sim_mock_id", "final_tower_state.json")
        }
    }
    mock_load_json.return_value = {"ok": True, "payload": {"floor_memory": [{"floor_id": 2}]}}
    mock_make_diff_report.return_value = {"ok": True, "payload": {"changed": True, "changes": {"mutation_level_delta": 1, "new_unclaimed_survivor_marks": ["mark_new"]}, "readable_summary": ["summary"]}}
    mock_write_diff_report.return_value = {"ok": True, "path": "mock_diff_path"}

    mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, debug=True)
    assert mock_make_event.called
    assert mock_write_event.called
    assert any("ReportStart" in event["args"] for event in mock_make_event.call_args_list)
    assert any("DiffReportStart" in event["args"] for event in mock_make_event.call_args_list)

@patch('engine.reports.runtime.mvp_end_to_end_report._debug_logger_available', False)
@patch('builtins.print')
@patch('engine.reports.runtime.mvp_end_to_end_report._mvp_components_available', True)
@patch('engine.reports.runtime.mvp_end_to_end_report._replay_floor_diff_reporter_available', True)
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_startup_orchestrator.startup_mvp_runtime')
@patch('engine.reports.runtime.mvp_end_to_end_report.mvp_scripted_simulation.run_scripted_simulation')
@patch('engine.reports.runtime.mvp_end_to_end_report.json_save_manager.load_json')
@patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.make_replay_floor_diff_report')
@patch('engine.reports.runtime.mvp_end_to_end_report.replay_floor_diff_reporter.write_replay_floor_diff_report')
def test_report_functional_without_debug_logger(
    mock_write_diff_report, mock_make_diff_report, mock_load_json,
    mock_run_simulation, mock_startup_runtime, mock_print, setup_teardown_test_dir
):
    mock_startup_runtime.return_value = {"ok": True, "errors": [], "tower_state": tower_state_bootstrapper.make_default_tower_state()}
    mock_run_simulation.return_value = {
        "ok": True, "payload": {
            "ok": True, "steps_executed": 1, "errors": [],
            "final_tower_state_path": os.path.join(SIMULATIONS_SAVE_DIR, "sim_mock_id", "final_tower_state.json")
        }
    }
    mock_load_json.return_value = {"ok": True, "payload": {"floor_memory": [{"floor_id": 2}]}}
    mock_make_diff_report.return_value = {"ok": True, "payload": {"changed": True, "changes": {"mutation_level_delta": 1, "new_unclaimed_survivor_marks": ["mark_new"]}, "readable_summary": ["summary"]}}
    mock_write_diff_report.return_value = {"ok": True, "path": "mock_diff_path"}

    result = mvp_end_to_end_report.run_mvp_end_to_end_report(output_dir=REPORTS_OUTPUT_DIR, debug=True)
    assert result["ok"] is True
    mock_print.assert_any_call("WARNING: Debugging is enabled but debug_logger is unavailable. Event: Starting MVP end-to-end report generation.")