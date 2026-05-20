import pytest
from engine.console.runtime import mvp_text_console

def test_console_route_visibility_status():
    res = mvp_text_console.run_console_script(["status"])
    assert res[0]["ok"]
    assert "Route Recon:" in res[0]["message"]
    payload = res[0]["payload"]
    assert "route_visibility" in payload
    assert payload["route_visibility"]["best_visibility_band"] is not None
