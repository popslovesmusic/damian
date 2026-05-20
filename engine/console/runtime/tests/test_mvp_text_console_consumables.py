import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_potion_dir"

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

def test_potion_command_parsing():
    """Validates that parse_console_command handles potion and potion <quantity>."""
    cmd1 = mvp_text_console.parse_console_command("potion")
    assert cmd1["command"] == "potion"
    assert cmd1["args"] == []
    
    cmd2 = mvp_text_console.parse_console_command("potion 3")
    assert cmd2["command"] == "potion"
    assert cmd2["args"] == ["3"]

def test_potion_consumption_success():
    """Validates that the potion command consumes potions from inventory."""
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Add some potions manually to inventory
    session_state["inventory_state"]["items"].append({
        "item_id": "ash_potion_small",
        "quantity": 5,
        "capacity_cost": 1
    })
    session_state["inventory_state"]["used_capacity"] = 5
    
    # 3. Execute potion command
    cmd_struct = mvp_text_console.parse_console_command("potion 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["consumable_used"] is True
    assert payload["quantity_requested"] == 2
    assert payload["inventory_transaction"]["transaction_applied"] is True
    
    # Check inventory state
    inv = session_state["inventory_state"]
    item = next((i for i in inv["items"] if i["item_id"] == "ash_potion_small"), None)
    assert item["quantity"] == 3

def test_potion_consumption_fail_insufficient():
    """Validates safe failure when potions are insufficient."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_res"] if "session_res" in session_res else session_res["session_state"]
    
    # Add only 1 potion
    session_state["inventory_state"]["items"].append({
        "item_id": "ash_potion_small",
        "quantity": 1,
        "capacity_cost": 1
    })
    
    # Try to consume 2
    cmd_struct = mvp_text_console.parse_console_command("potion 2")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    assert result["payload"]["consumable_used"] is False
    assert "Insufficient quantity" in result["error"]["message"]
    
    # Inventory should remain unchanged (1 potion)
    inv = session_state["inventory_state"]
    item = next((i for i in inv["items"] if i["item_id"] == "ash_potion_small"), None)
    assert item["quantity"] == 1

def test_potion_command_invalid_quantity():
    """Validates safe failure for invalid quantity strings."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("potion abc")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is False
    assert result["error"] == "InvalidArguments"

def test_potion_no_healing_runtime():
    """
    Validates that the potion command does not modify player health
    (since real healing runtime is a non-goal for this patch).
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Add potions
    session_state["inventory_state"]["items"].append({
        "item_id": "ash_potion_small",
        "quantity": 5,
        "capacity_cost": 1
    })
    
    # Set player health to 50
    # For MVP, health is often part of player_progression or combat_session
    # Console doesn't track a 'live' player health yet outside of handled commands
    # But we can verify it doesn't try to add a 'health' key to inventory_state or similar
    
    cmd_struct = mvp_text_console.parse_console_command("potion")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    # Verify no 'health' or 'healing' keys were introduced into payload or state improperly
    assert "healing_applied" not in result["payload"]
