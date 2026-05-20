import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_repair_runtime_dir"

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

def test_repair_command_restores_durability_success():
    """
    Validates that the repair command restores equipment durability
    and consumes materials.
    """
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Add materials to inventory
    session_state["inventory_state"]["items"].append({
        "item_id": "repair_material_basic",
        "quantity": 10,
        "capacity_cost": 1
    })
    
    # 3. Damage an item in the loadout
    item = session_state["equipment_loadout"]["equipped_items"][0]
    initial_durability = 50
    item["durability"]["current"] = initial_durability
    
    # 4. Execute repair command
    cmd_struct = mvp_text_console.parse_console_command("repair 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["repair_applied"] is True
    assert payload["durability_restored"] == 20
    assert "repair_event" in payload
    assert "inventory_transaction" in payload
    
    # Check updated state
    updated_item = session_state["equipment_loadout"]["equipped_items"][0]
    assert updated_item["durability"]["current"] == 70
    
    # Check inventory
    inv = session_state["inventory_state"]
    mat = next((i for i in inv["items"] if i["item_id"] == "repair_material_basic"), None)
    assert mat["quantity"] == 8

def test_repair_command_fail_insufficient_materials():
    """Validates safe failure when materials are missing."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Ensure bag is empty of materials
    session_state["inventory_state"]["items"] = []
    
    # Damage item
    item = session_state["equipment_loadout"]["equipped_items"][0]
    item["durability"]["current"] = 50
    
    cmd_struct = mvp_text_console.parse_console_command("repair 1")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    assert result["payload"]["repair_applied"] is False
    assert "not found" in result["error"]["message"]
    
    # Condition should be unchanged
    assert session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] == 50

def test_repair_command_no_repairable_item():
    """Validates message when all items are at max durability."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # All items at max (default)
    for item in session_state["equipment_loadout"]["equipped_items"]:
        item["durability"]["current"] = item["durability"]["maximum"]
        
    cmd_struct = mvp_text_console.parse_console_command("repair")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "maximum durability" in result["message"]
    assert result["payload"]["repair_applied"] is False

def test_repair_command_persists_loadout():
    """Validates that updated loadout is stored in session state."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Add materials and damage
    session_state["inventory_state"]["items"].append({"item_id": "repair_material_basic", "quantity": 1})
    session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] = 10
    
    mvp_text_console.execute_console_command(session_state, {"command": "repair", "args": []}, debug=True)
    
    # Verify session state updated
    assert session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] == 20
