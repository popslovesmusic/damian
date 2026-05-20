import pytest
from engine.dashboard.domain import domain_dashboard_snapshot_builder
from engine.console.runtime import mvp_text_console

def test_dashboard_route_visibility():
    session_result = mvp_text_console.start_console_session()
    session_state = session_result["session_state"]
    
    snapshot_res = domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot(session_state)
    assert snapshot_res["ok"]
    
    snapshot = snapshot_res["snapshot"]
    assert "route_visibility_summary" in snapshot
    vis_summary = snapshot["route_visibility_summary"]
    
    assert "average_information_accuracy" in vis_summary
    assert "best_visibility_band" in vis_summary
    assert "reconnaissance_level" in vis_summary
