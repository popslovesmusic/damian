import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator
from engine.domain.ownership import domain_claim_stub

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_domain_claim_dir"

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

def test_claim_command_default():
    """Validates default domain claim creation."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("claim")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["domain_claim_created"] is True
    assert payload["domain_claim"]["claim_type"] == "recovery_anchor"
    assert "maintenance_pressure" in payload
    assert payload["tower_hostility_preserved"] is True
    
    # Verify persistence in session
    assert len(session_state["domain_claims"]) == 1
    assert session_state["last_domain_claim"]["claim_id"] == payload["domain_claim"]["claim_id"]

def test_claim_command_specific_type():
    """Validates specific domain claim creation."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("claim repair_station")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert result["payload"]["domain_claim"]["claim_type"] == "repair_station"

def test_claim_command_polymorphic_mark():
    """Validates legacy survivor mark claim behavior."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Manually add a mark to floor memory for testing
    tower_state = session_state["runtime_context"]["tower_state"]
    from engine.residue.runtime import mvp_residue_writer
    fm = mvp_residue_writer.get_or_create_floor_memory(tower_state, 1)["payload"]
    fm["unclaimed_easter_eggs"].append("test_mark_1")
    
    cmd_struct = mvp_text_console.parse_console_command("claim test_mark_1")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    assert "Mark test_mark_1 claimed" in result["message"]
    # Domain claims shouldn't have been created
    assert len(session_state["domain_claims"]) == 0

def test_dashboard_reflects_claims():
    """Validates that dashboard status reflects created claims."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 1. Create claim
    mvp_text_console.execute_console_command(session_state, {"command": "claim", "args": ["supply_cache"]}, debug=True)
    
    # 2. Check status
    res = mvp_text_console.execute_console_command(session_state, {"command": "status", "args": []}, debug=True)
    
    snapshot = res["payload"]["dashboard_snapshot"]
    assert snapshot["domain_claim_summary"]["active_claims"] == 1
    assert "Claims (1 active)" in res["payload"]["dashboard_summary"]

def test_invalid_claim_type_is_treated_as_mark():
    """Validates that unknown claim types are treated as mark IDs and fail safely if mark doesn't exist."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    cmd_struct = mvp_text_console.parse_console_command("claim fake_type")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    # Should fail as mark 'fake_type' doesn't exist
    assert result["ok"] is False
    assert result["error"] in ["DiscoveryFailed", "ClaimFailed", "MarkNotFound", "MarkNotDiscovered"] # Depending on mark system response
