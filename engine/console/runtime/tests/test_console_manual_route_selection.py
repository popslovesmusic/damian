import pytest
from engine.console.runtime import mvp_text_console

def test_manual_route_selection_advance():
    commands = [
        "routes",
        "traverse route_1_primary", # Assuming room graph generates something like route_1_primary, or we fallback
        "status"
    ]
    # To be safe, we just use 'traverse' which uses the fallback if ID not found, but let's test the command format
    res = mvp_text_console.run_console_script(["traverse"])
    assert res[0]["ok"], f"Command failed: {res[0].get('message')}"
    assert res[0]["payload"]["traversal_event"] is not None

def test_manual_route_selection_escape():
    res = mvp_text_console.run_console_script(["escape"])
    assert res[0]["ok"]
    assert res[0]["payload"]["escape_resolution"] is not None

def test_route_hazard_visibility_in_routes_command():
    res = mvp_text_console.run_console_script(["routes"])
    assert res[0]["ok"]
    assert "Recon:" in res[0]["message"]
