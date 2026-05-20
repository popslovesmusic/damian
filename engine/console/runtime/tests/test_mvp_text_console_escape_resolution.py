import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_escape_resolution_dir"

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

def test_escape_command_resolves_success():
    """Validates successful escape attempt."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    # Floor 1, low risk
    session_state["inventory_state"]["used_capacity"] = 0
    
    cmd_struct = mvp_text_console.parse_console_command("escape")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert "escape_resolution" in payload
    assert payload["escape_outcome"] == "ESCAPE_SUCCESS"
    assert payload["pipeline_outcome"] == "RETREAT_TO_HUB"
    assert payload["residue_written"] is True
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 0

def test_escape_command_resolves_partial(monkeypatch):
    """Validates partial escape with minor gold loss."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Mock traversal pressure to force Risk in partial range (0.3 < risk <= 0.6)
    # risk = tp*0.7 + re*0.3 - em. 
    # If re=0.1, em=0.25, and we want risk=0.4:
    # 0.4 = tp*0.7 + 0.03 - 0.25 => tp*0.7 = 0.62 => tp = 0.88
    from engine.traversal.runtime import traversal_pressure_stub
    monkeypatch.setattr(traversal_pressure_stub, "calculate_traversal_pressure", lambda *args, **kwargs: 0.88)
    
    cmd_struct = mvp_text_console.parse_console_command("escape")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["escape_outcome"] == "ESCAPE_PARTIAL"
    assert payload["resource_loss"]["gold"] == 100.0

def test_escape_command_resolves_retreat_drop(monkeypatch):
    """Validates severe escape failure causing DEFEAT_DROP."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    session_state["runtime_context"]["tower_state"]["current_floor"] = 2
    
    # Force very high risk and exposure.
    # Risk > 0.8 AND exposure >= 0.7 triggers RETREAT_DROP
    from engine.traversal.runtime import traversal_pressure_stub
    monkeypatch.setattr(traversal_pressure_stub, "calculate_traversal_pressure", lambda *args, **kwargs: 1.0)
    monkeypatch.setattr(traversal_pressure_stub, "calculate_escape_risk", lambda *args, **kwargs: 0.95)
    
    # We also need route_exposure >= 0.7 in the traversal_event
    # make_traversal_event usually gets it from route.
    # We'll mock make_traversal_event to return the exact event we need.
    original_make = traversal_pressure_stub.make_traversal_event
    def mock_make(*args, **kwargs):
        res = original_make(*args, **kwargs)
        if res["ok"]:
            res["traversal_event"]["escape_risk"] = 0.95
            res["traversal_event"]["route_exposure"] = 0.8
        return res
    monkeypatch.setattr(traversal_pressure_stub, "make_traversal_event", mock_make)
    
    cmd_struct = mvp_text_console.parse_console_command("escape")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["payload"]["escape_outcome"] == "ESCAPE_FAILED_RETREAT_DROP"
    assert result["payload"]["pipeline_outcome"] == "DEFEAT_DROP"
    assert result["payload"]["mutation_applied"] is True
    assert session_state["runtime_context"]["tower_state"]["current_floor"] == 1


def test_escape_command_preserves_safety_flags():
    """Validates that escape consequences are bounded."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    result = mvp_text_console.execute_console_command(session_state, {"command": "escape", "args": []}, debug=True)
    payload = result["payload"]
    
    assert payload["recoverability_preserved"] is True
    assert payload["floor_identity_preserved"] is True

def test_debug_safety():
    """Validates that debug=True doesn't break logic."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    mvp_text_console.execute_console_command(session_state, {"command": "escape", "args": []}, debug=True)
