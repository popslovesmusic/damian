import os
import json
import pytest
import shutil
import tempfile
from engine.console.runtime import mvp_text_console
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
            
    yield paths
    shutil.rmtree(temp_dir)

def test_parse_combat_command():
    cmd = mvp_text_console.parse_console_command("combat dangerous")
    assert cmd["command"] == "combat"
    assert cmd["args"] == ["dangerous"]
    
    cmd = mvp_text_console.parse_console_command("combat")
    assert cmd["command"] == "combat"
    assert cmd["args"] == []

def test_execute_combat_safe(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("combat safe")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert result["payload"]["resolved_outcome"] == "VICTORY_ASCEND"
    assert result["payload"]["pipeline_result"]["current_floor"] == 2

def test_execute_combat_dangerous(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("combat dangerous")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert result["payload"]["resolved_outcome"] == "DEFEAT_DROP"
    assert result["payload"]["mutation_applied"] is True
    assert result["payload"]["survivor_mark_attached"] is True
    assert session_state["latest_diff"] is not None

def test_execute_combat_exhausted(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("combat exhausted")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert result["payload"]["resolved_outcome"] == "RETREAT_TO_HUB"

def test_combat_no_bypass_residue(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("combat safe"))
    
    tower_state = session_state["runtime_context"]["tower_state"]
    # Check that floor 1 has a residue record in history
    floor_1_memory = next((fm for fm in tower_state["floor_memory"] if fm["floor_id"] == 1), None)
    assert floor_1_memory is not None
    assert len(floor_1_memory["residue_history"]) > 0
    assert floor_1_memory["residue_history"][0]["outcome"] == "VICTORY_ASCEND"

def test_combat_debug_mode(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths, debug=True)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("combat safe")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    assert result["ok"] is True
