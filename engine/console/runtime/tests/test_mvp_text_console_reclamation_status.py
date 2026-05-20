import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_reclamation_status_dir"

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

def test_status_command_includes_reclamation_pressure():
    """Validates that the status command includes reclamation evidence."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Establish claim to generate visibility
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": ["survivor_outpost"]}, debug=True)
    
    # 2. Check status
    cmd_struct = mvp_text_console.parse_console_command("status")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    
    assert "reclamation_pressure" in payload
    assert payload["reclamation_pressure"]["total_reclamation_pressure"] > 0
    assert "Reclamation:" in result["payload"]["dashboard_summary"]

def test_status_command_reflects_decay_irritation():
    """Validates that decaying footholds increase reclamation pressure in status."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Create claim
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": []}, debug=True)
    
    # 2. Get baseline reclamation
    res1 = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    base_reclamation = res1["payload"]["reclamation_pressure"]["total_reclamation_pressure"]
    
    # 3. Trigger decay via maintain (fail with 0 shards)
    session_state["inventory_state"]["currency"]["stability_shards"] = 0.0
    mvp_text_console.execute_console_command(session_state, {"command": "maintain", "args": []}, debug=True)
    
    # 4. Check new reclamation
    res2 = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    new_reclamation = res2["payload"]["reclamation_pressure"]["total_reclamation_pressure"]
    
    # Decaying claim should increase reclamation pressure
    assert new_reclamation > base_reclamation
