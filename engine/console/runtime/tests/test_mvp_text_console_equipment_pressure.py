import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_eq_dir"

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

def test_combat_command_uses_equipment_pressure():
    """
    Validates that the combat command includes equipment loadout and pressure
    in the response payload.
    """
    results = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    
    assert results[0]["ok"] is True
    payload = results[0]["payload"]
    
    # Core equipment fields
    assert "equipment_loadout" in payload
    assert "equipment_pressure" in payload
    assert payload["equipment_pressure_used"] is True
    
    # Observability fields
    assert "repair_pressure_observed" in payload
    assert "equipment_residue_visibility_observed" in payload
    assert "equipment_mutation_affinity_observed" in payload
    
    # Example loadout should have some pressure
    eq_p = payload["equipment_pressure"]
    assert 0.0 <= eq_p["repair_pressure"] <= 1.0
    assert 0.0 <= eq_p["residue_visibility"] <= 1.0

def test_combat_variants_remain_functional():
    """Validates that variants still produce expected outcomes with equipment active."""
    # Safe -> Victory
    res_safe = mvp_text_console.run_console_script(["combat safe"], paths=_get_test_paths(), debug=True)
    assert res_safe[0]["payload"]["resolved_outcome"] == "VICTORY_ASCEND"
    
    # Dangerous -> Defeat (usually)
    res_dang = mvp_text_console.run_console_script(["combat dangerous"], paths=_get_test_paths(), debug=True)
    assert res_dang[0]["payload"]["resolved_outcome"] == "DEFEAT_DROP"
    
    # Exhausted -> Retreat
    res_exh = mvp_text_console.run_console_script(["combat exhausted"], paths=_get_test_paths(), debug=True)
    assert res_exh[0]["payload"]["resolved_outcome"] == "RETREAT_TO_HUB"

def test_defeat_still_triggers_pipeline():
    """Validates that DEFEAT_DROP with equipment still triggers mutation evidence."""
    # Force a defeat
    results = mvp_text_console.run_console_script(["combat dangerous"], paths=_get_test_paths(), debug=True)
    payload = results[0]["payload"]
    
    if payload["resolved_outcome"] == "DEFEAT_DROP":
        assert "pipeline_result" in payload
        assert "mutation_applied" in payload
        assert "survivor_mark_attached" in payload
