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

def test_start_console_session(temp_paths):
    result = mvp_text_console.start_console_session(paths=temp_paths)
    assert result["ok"] is True
    assert "session_state" in result
    assert result["session_state"]["session_active"] is True

def test_parse_console_command():
    cmd = mvp_text_console.parse_console_command("claim mark_1_1")
    assert cmd["command"] == "claim"
    assert cmd["args"] == ["mark_1_1"]
    
    cmd = mvp_text_console.parse_console_command("  STATUS  ")
    assert cmd["command"] == "status"
    assert cmd["args"] == []

def test_execute_status(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("status")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert "Floor: 1" in result["message"]
    assert result["payload"]["current_floor"] == 1

def test_execute_ascend(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("ascend")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert "New floor: 2" in result["message"]
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 2

def test_execute_defeat_and_diff(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    # Defeat on floor 1 stays on floor 1 and mutates it
    cmd_struct = mvp_text_console.parse_console_command("defeat")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert "New floor: 1" in result["message"]
    assert session_state["latest_diff"] is not None
    
    # Check diff command
    diff_result = mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("diff"))
    assert diff_result["ok"] is True
    # The diff summary should show mutation level increase
    assert "Mutation level increased" in diff_result["message"]

def test_execute_marks_and_claim(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    # Trigger defeat to create a mark
    mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("defeat"))
    
    # marks command
    marks_result = mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("marks"))
    assert marks_result["ok"] is True
    assert len(marks_result["payload"]) > 0
    mark_id = marks_result["payload"][0]
    
    # claim command
    claim_result = mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("claim " + mark_id))
    assert claim_result["ok"] is True
    assert "claimed!" in claim_result["message"]
    
    # claim missing mark
    fail_claim = mvp_text_console.execute_console_command(session_state, mvp_text_console.parse_console_command("claim non_existent"))
    assert fail_claim["ok"] is False
    assert fail_claim["error"] == "MarkNotDiscovered"

def test_execute_save(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("save")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert os.path.exists(temp_paths["tower_state"])

def test_execute_quit(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("quit")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is True
    assert session_state["session_active"] is False

def test_run_console_script(temp_paths):
    commands = ["status", "ascend", "ascend", "defeat", "diff", "marks", "quit"]
    results = mvp_text_console.run_console_script(commands, paths=temp_paths)
    
    assert len(results) == len(commands)
    assert all(r["ok"] for r in results)
    assert results[3]["payload"]["current_floor"] == 2 # 1 -> 2 -> 3 -> 2
    assert results[4]["command"] == "diff"

def test_invalid_command(temp_paths):
    session_result = mvp_text_console.start_console_session(paths=temp_paths)
    session_state = session_result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("invalid_cmd")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct)
    
    assert result["ok"] is False
    assert result["error"] == "UnknownCommand"

def test_debug_mode(temp_paths):
    # Just ensure it doesn't crash with debug=True
    result = mvp_text_console.start_console_session(paths=temp_paths, debug=True)
    assert result["ok"] is True
    session_state = result["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("status")
    res = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    assert res["ok"] is True
