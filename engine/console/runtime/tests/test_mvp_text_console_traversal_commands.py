import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_traversal_commands_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def _get_test_paths():
    paths = mvp_startup_orchestrator.make_default_runtime_paths()
    paths["tower_state"] = os.path.join(TEST_DIR, "tower_state.json")
    paths["player_progression"] = os.path.join(TEST_DIR, "player_progression.json")
    paths["domain_state"] = os.path.join(TEST_DIR, "domain_state.json")
    return paths

def test_advance_command_traverses_floor():
    """
    Validates that the 'advance' command calculates pressure and moves
    the player to the next floor.
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    initial_floor = session_state["runtime_context"]["tower_state"]["current_floor"]
    
    cmd_struct = mvp_text_console.parse_console_command("advance")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "advance" in result["message"]
    
    payload = result["payload"]
    assert "traversal_event" in payload
    assert "traversal_pressure" in payload
    assert "escape_risk" in payload
    assert "pipeline_result" in payload
    
    # Check state update
    new_floor = session_state["runtime_context"]["tower_state"]["current_floor"]
    assert new_floor == initial_floor + 1

def test_escape_command_retreats_to_hub():
    """
    Validates that the 'escape' command calculates pressure and moves
    the player back to the hub (floor 0).
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    # Move to floor 2 first
    session_state["runtime_context"]["tower_state"]["current_floor"] = 2
    
    cmd_struct = mvp_text_console.parse_console_command("escape")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "ESCAPE_SUCCESS" in result["message"]
    assert "Returned to Hub" in result["message"]
    
    # Check state update
    new_floor = session_state["runtime_context"]["tower_state"]["current_floor"]
    assert new_floor == 0

def test_advance_respects_floor_cap():
    """Validates that advance respects the MVP three-floor cap."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Move to floor 3
    session_state["runtime_context"]["tower_state"]["current_floor"] = 3
    
    cmd_struct = mvp_text_console.parse_console_command("advance")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    # Outcome pipeline should block floor 4
    assert result["ok"] is False
    assert "maximum" in result["message"]

def test_legacy_commands_still_work():
    """Validates that 'ascend' and 'retreat' still function."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Test ascend
    res1 = mvp_text_console.execute_console_command(session_state, {"command": "ascend", "args": []}, debug=True)
    assert res1["ok"] is True
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 2
    
    # Test retreat
    res2 = mvp_text_console.execute_console_command(session_state, {"command": "retreat", "args": []}, debug=True)
    assert res2["ok"] is True
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 0

def test_traversal_command_payload_structure():
    """Validates the structured payload of traversal commands."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    result = mvp_text_console.execute_console_command(session_state, {"command": "advance", "args": []}, debug=True)
    payload = result["payload"]
    
    assert isinstance(payload["traversal_pressure"], float)
    assert isinstance(payload["escape_risk"], float)
    assert isinstance(payload["route_exposure"], float)
    assert payload["traversal_event"]["traversal_type"] == "advance"
