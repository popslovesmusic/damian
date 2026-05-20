import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator
from engine.dashboard.domain import domain_dashboard_snapshot_builder

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_dashboard_status_dir"

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

def test_status_command_includes_dashboard_snapshot():
    """
    Validates that the status command includes the domain dashboard snapshot
    and summary in its payload.
    """
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Execute status command
    cmd_struct = mvp_text_console.parse_console_command("status")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    
    # Verify dashboard additions (TOWER-ENGINE-106)
    assert "dashboard_snapshot" in payload
    assert "dashboard_summary" in payload
    assert payload["dashboard_snapshot_available"] is True
    
    snapshot = payload["dashboard_snapshot"]
    # Basic schema check
    assert "snapshot_id" in snapshot
    assert "pressure_summary" in snapshot
    assert "resource_summary" in snapshot
    
    # Verify existing status fields are preserved
    assert "current_floor" in payload
    assert "highest_floor" in payload
    assert "residue_count" in payload

def test_status_command_non_modifying():
    """Validates that checking status does not mutate session state."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. First run to trigger any lazy initialization (like floor memory)
    mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    
    # 2. Capture "stable" state
    initial_tower = json.dumps(session_state["runtime_context"]["tower_state"], sort_keys=True)
    initial_inv = json.dumps(session_state["inventory_state"], sort_keys=True)
    
    # 3. Second run
    mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    
    # 4. Verify no mutation between stable runs
    after_tower = json.dumps(session_state["runtime_context"]["tower_state"], sort_keys=True)
    after_inv = json.dumps(session_state["inventory_state"], sort_keys=True)
    
    assert initial_tower == after_tower
    assert initial_inv == after_inv

def test_dashboard_snapshot_validation_in_console():
    """Validates that the console snapshot matches the schema."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    result = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    snapshot = result["payload"]["dashboard_snapshot"]
    
    # Use builder's validation logic
    valid_res = domain_dashboard_snapshot_builder.validate_dashboard_snapshot(snapshot)
    assert valid_res["ok"] is True
