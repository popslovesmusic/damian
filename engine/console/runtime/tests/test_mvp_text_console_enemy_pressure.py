import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.save.runtime import json_save_manager
from engine.save.bootstrap import tower_state_bootstrapper

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_pressure_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_combat_command_uses_enemy_pressure_selector():
    """
    Validates that the combat command selects an enemy pressure profile
    and includes it in the payload.
    """
    from engine.core.orchestrator import mvp_startup_orchestrator
    paths = mvp_startup_orchestrator.make_default_runtime_paths()
    
    # Override only what's needed for tests
    paths["tower_state"] = os.path.join(TEST_DIR, "tower_state.json")
    paths["player_progression"] = os.path.join(TEST_DIR, "player_progression.json")
    paths["domain_state"] = os.path.join(TEST_DIR, "domain_state.json")
    
    # Run combat safe
    results = mvp_text_console.run_console_script(["combat safe"], paths=paths, debug=True)
    
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    assert "enemy_pressure_profile" in payload
    assert payload["enemy_pressure_profile_used"] is True
    assert "enemy_archetype_id" in payload
    assert "enemy_adaptation_reasoning" in payload
    assert isinstance(payload["enemy_adaptation_reasoning"], list)
    assert len(payload["enemy_adaptation_reasoning"]) > 0

def test_combat_safe_victory():
    """Validates that 'combat safe' can result in VICTORY_ASCEND."""
    results = mvp_text_console.run_console_script(["combat safe"], debug=True)
    assert results[0]["ok"] is True
    assert results[0]["payload"]["resolved_outcome"] == "VICTORY_ASCEND"

def test_combat_dangerous_defeat():
    """Validates that 'combat dangerous' can result in DEFEAT_DROP."""
    results = mvp_text_console.run_console_script(["combat dangerous"], debug=True)
    assert results[0]["ok"] is True
    assert results[0]["payload"]["resolved_outcome"] == "DEFEAT_DROP"

def test_combat_exhausted_retreat():
    """Validates that 'combat exhausted' can result in RETREAT_TO_HUB."""
    results = mvp_text_console.run_console_script(["combat exhausted"], debug=True)
    assert results[0]["ok"] is True
    assert results[0]["payload"]["resolved_outcome"] == "RETREAT_TO_HUB"

def test_combat_defeat_triggers_pipeline():
    """
    Validates that DEFEAT_DROP from combat triggers mutation and survivor marks
    as seen in the payload.
    """
    results = mvp_text_console.run_console_script(["combat dangerous"], debug=True)
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    if payload["resolved_outcome"] == "DEFEAT_DROP":
        assert "pipeline_result" in payload
        assert "mutation_applied" in payload
        assert "survivor_mark_attached" in payload
        # Note: Depending on RNG, these might be False, but the fields should exist

def test_combat_pressure_observable_in_debug():
    """Validates that pressure evidence is observable when debug=True."""
    results = mvp_text_console.run_console_script(["combat safe"], debug=True)
    payload = results[0]["payload"]
    
    assert "resource_pressure_observed" in payload
    assert "residue_pressure_observed" in payload
