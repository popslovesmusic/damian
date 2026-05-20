import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_repair_dir"

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

def test_repair_command_parsing():
    """Validates that parse_console_command handles repair and repair <quantity>."""
    cmd1 = mvp_text_console.parse_console_command("repair")
    assert cmd1["command"] == "repair"
    assert cmd1["args"] == []
    
    cmd2 = mvp_text_console.parse_console_command("repair 3")
    assert cmd2["command"] == "repair"
    assert cmd2["args"] == ["3"]

def test_repair_material_deduction_success():
    """Validates that the repair command deducts materials and restores durability."""
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Add some repair materials manually to inventory
    session_state["inventory_state"]["items"].append({
        "item_id": "repair_material_basic",
        "quantity": 5,
        "capacity_cost": 1
    })
    session_state["inventory_state"]["used_capacity"] = 5

    # 3. Damage an item (TOWER-ENGINE-082 requires damage for restoration)
    session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] = 50
    
    # 4. Execute repair command
    cmd_struct = mvp_text_console.parse_console_command("repair 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["repair_applied"] is True
    assert payload["quantity_requested"] == 2
    assert payload["durability_restored"] == 20
    assert payload["inventory_transaction"]["transaction_applied"] is True
    
    # Check inventory state
    inv = session_state["inventory_state"]
    item = next((i for i in inv["items"] if i["item_id"] == "repair_material_basic"), None)
    assert item["quantity"] == 3

def test_repair_consumption_fail_insufficient():
    """Validates safe failure when repair materials are insufficient."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Add only 1 material
    session_state["inventory_state"]["items"].append({
        "item_id": "repair_material_basic",
        "quantity": 1,
        "capacity_cost": 1
    })

    # Damage item
    session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] = 50
    
    # Try to deduct 2
    cmd_struct = mvp_text_console.parse_console_command("repair 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    assert result["payload"]["repair_applied"] is False
    assert "Insufficient" in result["error"]["message"]
    
    # Inventory should remain unchanged (1 material)
    inv = session_state["inventory_state"]
    item = next((i for i in inv["items"] if i["item_id"] == "repair_material_basic"), None)
    assert item["quantity"] == 1

def test_repair_command_invalid_quantity():
    """Validates safe failure for invalid quantity strings."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("repair abc")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    assert result["error"] == "InvalidArguments"

def test_repair_restores_durability_now():
    """
    Validates that the repair command DOES modify equipment durability now
    (replaces old test that expected it not to).
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Add materials and damage
    session_state["inventory_state"]["items"].append({
        "item_id": "repair_material_basic",
        "quantity": 5,
        "capacity_cost": 1
    })
    session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"] = 50
    
    cmd_struct = mvp_text_console.parse_console_command("repair")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert result["payload"]["durability_restored"] == 10
    assert result["payload"]["durability_restored_flag"] is True

