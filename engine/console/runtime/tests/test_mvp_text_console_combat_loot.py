import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator
from engine.loot.runtime import mvp_loot_event_stub

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_loot_dir"

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

def test_combat_safe_includes_loot():
    """Validates that 'combat safe' includes loot event and summary."""
    results = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "loot_event" in payload
    assert "loot_summary" in payload
    assert "resource_sink_pressure" in payload
    assert "bounded_reward_flags" in payload
    
    # Check bounded rewards for VICTORY_ASCEND (safe is usually victory)
    if payload["resolved_outcome"] == "VICTORY_ASCEND":
        assert payload["loot_event"]["rewards"]["gold"] == 10000
    
    # Verify flags are all False
    flags = payload["bounded_reward_flags"]
    assert all(v is False for v in flags.values())

def test_combat_dangerous_includes_loot():
    """Validates that 'combat dangerous' includes loot event."""
    results = mvp_text_console.run_console_script(["combat dangerous"], paths=_get_test_paths(), debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "loot_event" in payload
    assert payload["loot_event"]["source"] == "combat_reward"

def test_combat_exhausted_includes_loot():
    """Validates that 'combat exhausted' includes loot event."""
    results = mvp_text_console.run_console_script(["combat exhausted"], paths=_get_test_paths(), debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "loot_event" in payload
    assert "resource_sink_pressure" in payload

def test_loot_event_validation():
    """Validates that the generated loot event matches the schema."""
    results = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    loot_event = results[0]["payload"]["loot_event"]
    
    validation = mvp_loot_event_stub.validate_loot_event(loot_event)
    assert validation["ok"] is True

def test_no_inventory_persistence_yet():
    """
    Validates that loot does not modify tower_state in a way that implies
    inventory persistence (since that's not implemented yet).
    """
    results = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    tower_state = results[0]["payload"]["pipeline_result"]["tower_state"]
    
    # Tower state should NOT have an 'inventory' key at this stage
    assert "inventory" not in tower_state
