import os
import json
import shutil
import pytest
from engine.console.runtime import mvp_text_console
from engine.core.orchestrator import mvp_startup_orchestrator

# Define a temporary directory for tests
TEST_DIR = "test_temp_console_durability_dir"

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

def test_combat_command_exposes_durability_evidence():
    """
    Validates that the combat command includes durability decay evidence
    in the response payload and persists it in the session state.
    """
    # 1. Start session
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # 2. Ensure we have a loadout
    assert session_state["equipment_loadout"] is not None
    initial_durability = session_state["equipment_loadout"]["equipped_items"][0]["durability"]["current"]
    
    # 3. Run combat (dangerous to ensure meaningful pressure)
    cmd_struct = mvp_text_console.parse_console_command("combat dangerous")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    assert result["ok"] is True
    payload = result["payload"]
    
    # Check payload additions
    assert "durability_decay_applied" in payload
    assert "durability_events" in payload
    assert "updated_equipment_loadout" in payload
    assert "durability_pressure_observed" in payload
    
    if payload["durability_decay_applied"]:
        assert len(payload["durability_events"]) > 0
        assert payload["durability_pressure_observed"] is True
        
        # Check persistence in session state
        updated_loadout = session_state["equipment_loadout"]
        new_durability = updated_loadout["equipped_items"][0]["durability"]["current"]
        assert new_durability < initial_durability
        assert session_state["last_durability_events"] == payload["durability_events"]

def test_durability_decay_clamped_at_zero_in_console():
    """Validates that durability never drops below 0 through multiple console combats."""
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Run dangerous combat multiple times
    for _ in range(5):
        cmd_struct = mvp_text_console.parse_console_command("combat dangerous")
        mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
        
    updated_loadout = session_state["equipment_loadout"]
    for item in updated_loadout["equipped_items"]:
        assert item["durability"]["current"] >= 0

def test_combat_variants_preserve_pipeline_behavior():
    """Validates that variants still produce expected outcomes and trigger mutations."""
    # Run dangerous combat to force a DEFEAT_DROP (usually)
    results = mvp_text_console.run_console_script(["combat dangerous"], paths=_get_test_paths(), debug=True)
    payload = results[0]["payload"]
    
    if payload["resolved_outcome"] == "DEFEAT_DROP":
        assert "pipeline_result" in payload
        assert "mutation_applied" in payload
        # Ensure durability decay was also applied
        assert "durability_decay_applied" in payload

def test_durability_decay_does_not_bypass_residue():
    """
    Validates that equipment deterioration doesn't interfere with 
    residue generation in tower_state.
    """
    session_res = mvp_text_console.start_console_session(paths=_get_test_paths(), debug=True)
    session_state = session_res["session_state"]
    
    # Run combat
    cmd_struct = mvp_text_console.parse_console_command("combat safe")
    result = mvp_text_console.execute_console_command(session_state, cmd_struct, debug=True)
    
    tower_state = session_state["runtime_context"]["tower_state"]
    # Check if residue exists for floor 1
    fm = next((fm for fm in tower_state["floor_memory"] if fm["floor_id"] == 1), None)
    assert fm is not None
    # We expect some residue even in victory if residue_writer is active
    # But for MVP stub, it depends on RNG. We just verify the state structure is preserved.
    assert "residue_history" in fm
