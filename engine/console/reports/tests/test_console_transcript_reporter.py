import os
import json
import pytest
import shutil
import tempfile
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator
from unittest.mock import patch

@pytest.fixture
def temp_paths():
    temp_dir = tempfile.mkdtemp()
    base_save_dir = os.path.join(temp_dir, 'saves', 'local_mvp')
    os.makedirs(base_save_dir, exist_ok=True)
    
    paths = mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=base_save_dir)
    # Ensure all paths are absolute
    for k, v in paths.items():
        if isinstance(v, str) and not os.path.isabs(v):
            paths[k] = os.path.abspath(v)
            
    yield paths, temp_dir
    shutil.rmtree(temp_dir)

def test_run_console_transcript_success(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts')
    # Use defeat on floor 1 to ensure target_floor == prev_floor for diffing
    commands = ["status", "defeat", "diff", "marks", "quit"]
    
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir
    )
    
    assert transcript["ok"] is True
    assert len(transcript["commands_executed"]) == len(commands)
    assert transcript["commands_requested"] == commands
    assert transcript["final_session_active"] is False
    assert transcript["mutation_observed"] is True
    assert transcript["survivor_mark_observed"] is True
    assert transcript["diff_observed"] is True
    
    # Check file exists
    files = os.listdir(output_dir)
    assert len(files) == 1
    assert files[0].endswith(".json")

def test_validate_console_transcript():
    valid_transcript = {
        "transcript_id": "test",
        "patch_id": "TOWER-ENGINE-040",
        "ok": True,
        "commands_requested": [],
        "commands_executed": [],
        "command_results": [],
        "final_session_active": False,
        "no_scope_creep_flags": {},
        "combat_sessions_observed": 0
    }
    assert console_transcript_reporter.validate_console_transcript(valid_transcript) is True
    
    invalid_transcript = {"patch_id": "wrong"}
    assert console_transcript_reporter.validate_console_transcript(invalid_transcript) is False

def test_summarize_console_transcript():
    transcript = {
        "transcript_id": "test-id",
        "ok": True,
        "commands_executed": ["status"],
        "commands_requested": ["status"],
        "final_floor": 1,
        "mutation_observed": True,
        "survivor_mark_observed": False,
        "diff_observed": True,
        "combat_sessions_observed": 0,
        "combat_victories_observed": 0,
        "combat_defeats_observed": 0,
        "combat_retreats_observed": 0,
        "resource_pressure_observed": False,
        "residue_pressure_observed": False
    }
    summary = console_transcript_reporter.summarize_console_transcript(transcript)
    assert "test-id" in summary
    assert "SUCCESS" in summary
    assert "Final Floor: 1" in summary
    assert "Mutation Observed: True" in summary

def test_debug_mode_safe(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts_debug')
    commands = ["status", "quit"]
    
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir, debug=True
    )
    assert transcript["ok"] is True

def test_startup_failure_transcript():
    # Mock startup to fail
    with patch('engine.core.orchestrator.mvp_startup_orchestrator.startup_mvp_runtime') as mock_startup:
        mock_startup.return_value = {"ok": False, "errors": [{"message": "Simulated Startup Failure"}]}
        
        transcript = console_transcript_reporter.run_console_transcript(["status"])
        assert transcript["ok"] is False
        assert "Simulated Startup Failure" in transcript["errors"][0]
        assert transcript["commands_executed"] == []
