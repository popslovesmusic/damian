import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_cap_dir"

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

def test_status_command_includes_capacity_pressure():
    """Validates that 'status' includes capacity pressure in payload."""
    results = mvp_text_console.run_console_script(["status"], paths=_get_test_paths(), debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "capacity_pressure_summary" in payload
    assert "capacity_pressure" in payload
    assert "capacity_band" in payload
    assert payload["capacity_pressure"] == 0.0
    assert payload["capacity_band"] == "EMPTY"

def test_combat_command_includes_capacity_pressure():
    """Validates that 'combat' includes updated capacity pressure after loot."""
    results = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "capacity_pressure_summary" in payload
    assert payload["capacity_pressure"] is not None
    # For MVP, victory gives materials which increment capacity
    assert payload["capacity_pressure"] >= 0.0

def test_potion_command_includes_capacity_pressure():
    """Validates that 'potion' includes updated capacity pressure."""
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Add potions
    session_state["inventory_state"]["items"].append({
        "item_id": "ash_potion_small",
        "quantity": 10,
        "capacity_cost": 1
    })
    session_state["inventory_state"]["used_capacity"] = 10
    
    # 3. Execute potion command
    cmd_struct = mvp_text_console.parse_console_command("potion 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert "capacity_pressure_summary" in payload
    # (10 - 2) / 40 = 0.2 (LOW)
    assert payload["capacity_pressure"] == 0.2
    assert payload["capacity_band"] == "LOW"

def test_repair_command_includes_capacity_pressure():
    """Validates that 'repair' includes updated capacity pressure."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Add materials
    session_state["inventory_state"]["items"].append({
        "item_id": "repair_material_basic",
        "quantity": 20,
        "capacity_cost": 1
    })
    session_state["inventory_state"]["used_capacity"] = 20
    
    # Execute repair command
    cmd_struct = mvp_text_console.parse_console_command("repair 4")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert "capacity_pressure_summary" in payload
    # (20 - 4) / 40 = 0.4 (MODERATE)
    assert payload["capacity_pressure"] == 0.4
    assert payload["capacity_band"] == "MODERATE"

def test_failed_potion_includes_capacity_pressure():
    """Validates that failed potion attempt still reports pre-transaction pressure."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Empty bag
    cmd_struct = mvp_text_console.parse_console_command("potion 1")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    payload = result["payload"]
    assert "capacity_pressure_summary" in payload
    assert payload["capacity_pressure"] == 0.0

def test_capacity_pressure_bounds():
    """Validates that capacity pressure remains between 0.0 and 1.0."""
    results = mvp_text_console.run_console_script(["status"], paths=_get_test_paths(), debug=True)
    payload = results[0]["payload"]
    assert 0.0 <= payload["capacity_pressure"] <= 1.0
