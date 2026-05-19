import os
import json
import pytest
import shutil
import tempfile
from engine.console.reports import console_transcript_reporter
from engine.core.orchestrator import mvp_startup_orchestrator

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

def test_run_combat_aware_transcript_victory(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts_combat')
    commands = ["status", "combat safe", "quit"]
    
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir
    )
    
    assert transcript["ok"] is True
    assert transcript["combat_sessions_observed"] == 1
    assert "VICTORY_ASCEND" in transcript["combat_outcomes_observed"]
    assert transcript["combat_victories_observed"] == 1
    assert transcript["final_floor"] == 2

def test_run_combat_aware_transcript_defeat(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts_combat_defeat')
    # Use dangerous variant to trigger defeat
    commands = ["combat dangerous", "diff", "marks", "quit"]
    
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir
    )
    
    assert transcript["ok"] is True
    assert transcript["combat_sessions_observed"] == 1
    assert "DEFEAT_DROP" in transcript["combat_outcomes_observed"]
    assert transcript["combat_defeats_observed"] == 1
    assert transcript["mutation_after_combat_observed"] is True
    assert transcript["survivor_mark_after_combat_observed"] is True
    assert transcript["diff_observed"] is True

def test_run_combat_aware_transcript_retreat(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts_combat_retreat')
    # Use exhausted variant to trigger retreat
    commands = ["combat exhausted", "quit"]
    
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir
    )
    
    assert transcript["ok"] is True
    assert transcript["combat_sessions_observed"] == 1
    assert "RETREAT_TO_HUB" in transcript["combat_outcomes_observed"]
    assert transcript["combat_retreats_observed"] == 1
    assert transcript["resource_pressure_observed"] is True

def test_residue_pressure_observation(temp_paths):
    paths, temp_dir = temp_paths
    output_dir = os.path.join(temp_dir, 'transcripts_pressure')
    
    # We don't have a direct variant for residue pressure > 0.5 yet, 
    # but we can mock or check if it's False by default.
    commands = ["combat safe", "quit"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir
    )
    assert transcript["residue_pressure_observed"] is False

def test_summarize_combat_transcript():
    transcript = {
        "transcript_id": "combat-id",
        "ok": True,
        "commands_executed": ["combat safe"],
        "commands_requested": ["combat safe"],
        "final_floor": 2,
        "mutation_observed": False,
        "survivor_mark_observed": False,
        "diff_observed": False,
        "combat_sessions_observed": 1,
        "combat_victories_observed": 1,
        "combat_defeats_observed": 0,
        "combat_retreats_observed": 0,
        "resource_pressure_observed": False,
        "residue_pressure_observed": True
    }
    summary = console_transcript_reporter.summarize_console_transcript(transcript)
    assert "Combat Sessions: 1 (V:1 D:0 R:0)" in summary
    assert "Residue Pressure Observed: True" in summary
