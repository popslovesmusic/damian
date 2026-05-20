import pytest
from engine.traversal.routes.route_hazard_visibility_stub import RouteVisibilitySnapshot

def test_route_visibility_snapshot():
    snapshot = RouteVisibilitySnapshot(
        route_id="route_1",
        visibility_level="low",
        environmental_cues=["Residue traces"],
        confirmed_hazards=[]
    )
    
    assert snapshot.route_id == "route_1"
    assert "Residue traces" in snapshot.environmental_cues
    
def test_invalid_visibility_level():
    with pytest.raises(ValueError):
        RouteVisibilitySnapshot(
            route_id="route_2",
            visibility_level="perfect",
            environmental_cues=[],
            confirmed_hazards=[]
        )