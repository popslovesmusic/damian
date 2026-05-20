import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_scarring_status_dir"

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

def test_status_includes_scarring_and_targeting():
    """Validates that status command payload includes scarring and targeting summaries."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Establish high-visibility foothold
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": ["survivor_outpost"]}, debug=True)
    
    # 2. Check status
    res = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    
    assert res["ok"] is True
    payload = res["payload"]
    
    assert "mutation_scarring" in payload
    assert payload["mutation_scarring"]["highest_scar_intensity"] > 0
    assert payload["mutation_scarring"]["scarred_nodes_count"] == 1
    
    assert "claim_targeting" in payload
    assert payload["claim_targeting"]["active_claims"] == 1
    assert "Scarring:" in res["payload"]["dashboard_summary"]

def test_claim_command_includes_targeting_evidence():
    """Validates that claim command result includes targeting and scarring evidence."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    res = mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": ["repair_station"]}, debug=True)
    
    assert res["ok"] is True
    payload = res["payload"]
    
    assert "targeting_pressure" in payload
    assert "local_scarring" in payload
    assert "maintenance_penalty" in payload
    assert "Targeting:" in res["message"]
