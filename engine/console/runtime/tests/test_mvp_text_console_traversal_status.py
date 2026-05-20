import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_traversal_status_dir"

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

def test_status_command_includes_traversal_evidence():
    """
    Validates that the status command includes traversal pressure and risk
    in its message and payload.
    """
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Add some pressure factors
    # Increase capacity pressure (e.g. 50%)
    session_state["inventory_state"]["used_capacity"] = 20
    session_state["inventory_state"]["inventory_capacity"] = 40
    
    # Simulate recent combat
    session_state["durability_pressure_observed"] = True
    
    # 3. Execute status command
    cmd_struct = mvp_text_console.parse_console_command("status")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "Traversal Risk" in result["message"]
    
    payload = result["payload"]
    assert "traversal_pressure" in payload
    assert "escape_risk" in payload
    assert "traversal_pressure_inputs" in payload
    
    inputs = payload["traversal_pressure_inputs"]
    assert inputs["capacity_pressure"] == 0.5
    assert inputs["combat_exposure"] == 0.5
    
    # Verify bounds
    assert 0.0 <= payload["traversal_pressure"] <= 1.0
    assert 0.0 <= payload["escape_risk"] <= 1.0

def test_status_command_does_not_modify_state():
    """Validates that checking status is a read-only operation."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    initial_floor = session_state["runtime_context"]["tower_state"]["current_floor"]
    initial_used = session_state["inventory_state"]["used_capacity"]
    
    mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == initial_floor
    assert session_state["inventory_state"]["used_capacity"] == initial_used

def test_status_reflects_mutation_pressure():
    """Validates that traversal risk increases with floor mutations."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Get base risk
    res1 = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    base_risk = res1["payload"]["escape_risk"]
    
    # Add a mutation manually to floor memory (floor_id is int in MVP)
    tower_state = session_state["runtime_context"]["tower_state"]
    floor_id = int(tower_state["current_floor"])
    found = False
    for fm in tower_state["floor_memory"]:
        if fm["floor_id"] == floor_id:
            fm["active_mutations"].append("test_mutation")
            found = True
            break
            
    if not found:
        # If not found, create it (should be created by status command already though)
        tower_state["floor_memory"].append({
            "floor_id": floor_id,
            "active_mutations": ["test_mutation"]
        })
            
    # Get new risk
    res2 = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    new_risk = res2["payload"]["escape_risk"]
    
    assert new_risk > base_risk
