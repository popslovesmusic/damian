from engine.traversal.routes.manual_route_selection_stub import RouteOption, RouteSelectionState

def test_route_selection():
    route1 = RouteOption(route_id="r1", target_node_id="n1", distance_cost=1, known_hazards=[])
    route2 = RouteOption(route_id="r2", target_node_id="n2", distance_cost=2, known_hazards=["spikes"])
    
    state = RouteSelectionState(current_node_id="start", available_routes=[route1, route2])
    
    assert state.selected_route_id is None
    
    # Select valid route
    success = state.select_route("r2")
    assert success is True
    assert state.selected_route_id == "r2"
    
    # Select invalid route
    success = state.select_route("r3")
    assert success is False
    assert state.selected_route_id == "r2"  # Remains unchanged