import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_room_route_traversal_dir"

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

def test_advance_command_uses_room_routes():
    """
    Validates that the 'advance' command builds a room graph,
    generates routes, and includes route evidence in the payload.
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("advance")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    
    # Verify room graph and routes (TOWER-ENGINE-095)
    assert "room_graph" in payload
    assert "room_routes" in payload
    assert len(payload["room_routes"]) > 0
    
    # Verify selected route
    assert "selected_route" in payload
    assert payload["route_pressure_used"] is True
    assert "environmental_profile" in payload
    assert "route_exposure" in payload
    
    # Verify pipeline routing
    assert payload["pipeline_result"]["outcome"] == "VICTORY_ASCEND"
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 2

def test_escape_command_uses_room_routes():
    """
    Validates that the 'escape' command builds a room graph
    and selects an appropriate route.
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    session_state["runtime_context"]["tower_state"]["current_floor"] = 2
    
    cmd_struct = mvp_text_console.parse_console_command("escape")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    
    assert "selected_route" in payload
    assert "escape_modifier" in payload
    assert payload["route_pressure_used"] is True
    
    # Verify pipeline routing
    assert payload["pipeline_result"]["outcome"] == "RETREAT_TO_HUB"
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 0

def test_traversal_command_recalculates_pressure_with_route():
    """Validates that route hazards influence traversal hazard in the payload."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    result = mvp_text_console.execute_console_command(session_state, {"command": "advance", "args": []}, debug=True)
    payload = result["payload"]
    
    # Hazard should be non-zero due to route exposure even if other factors are low
    assert payload["traversal_pressure"] > 0
    assert payload["traversal_event"]["traversal_pressure"]["total_pressure"] == payload["traversal_pressure"]

def test_advance_still_respects_floor_cap():
    """Validates that floor cap is still enforced with room route integration."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    session_state["runtime_context"]["tower_state"]["current_floor"] = 3
    
    result = mvp_text_console.execute_console_command(session_state, {"command": "advance", "args": []}, debug=True)
    assert result["ok"] is False
    assert "maximum" in result["message"]
