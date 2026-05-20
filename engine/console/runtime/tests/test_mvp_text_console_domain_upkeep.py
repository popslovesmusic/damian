import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_domain_upkeep_dir"

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

def test_maintain_command_no_claims():
    """Validates maintain command behavior when no claims exist."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("maintain")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "No footholds established" in result["message"]

def test_maintain_command_success():
    """Validates successful material upkeep for established claims."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Create a claim
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": []}, debug=True)
    assert len(session_state["domain_claims"]) == 1
    assert session_state["domain_claims"][0]["status"] == "ACTIVE"
    
    # Starting shards should be 10.0 (from start_console_session mock setup)
    initial_shards = session_state["inventory_state"]["currency"]["stability_shards"]
    assert initial_shards == 10.0
    
    # 2. Run maintenance
    cmd_struct = mvp_text_console.parse_console_command("maintain")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert result["payload"]["shards_consumed"] > 0
    assert session_state["domain_claims"][0]["status"] == "ACTIVE"
    
    # Verify material deduction
    new_shards = session_state["inventory_state"]["currency"]["stability_shards"]
    assert new_shards < initial_shards

def test_maintain_command_triggers_decay_on_empty_shards():
    """Validates that maintenance fails and triggers decay if shards are empty."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Create claim
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": []}, debug=True)
    
    # 2. Drain shards
    session_state["inventory_state"]["currency"]["stability_shards"] = 0.0
    
    # 3. Run maintenance
    cmd_struct = mvp_text_console.parse_console_command("maintain")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert result["payload"]["shards_consumed"] == 0
    # State should have decayed
    assert session_state["domain_claims"][0]["status"] == "DECAYING"

def test_maintain_command_restores_decayed_claim():
    """Validates that paying upkeep restores a decaying claim."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Setup decaying claim
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": []}, debug=True)
    session_state["domain_claims"][0]["status"] = "DECAYING"
    
    # 2. Ensure shards available
    session_state["inventory_state"]["currency"]["stability_shards"] = 10.0
    
    # 3. Run maintenance
    mvp_text_console.execute_console_command(session_state, {"command": "maintain", "args": []}, debug=True)
    
    # Should be back to ACTIVE
    assert session_state["domain_claims"][0]["status"] == "ACTIVE"
