from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RouteOption:
    route_id: str
    target_node_id: str
    distance_cost: int
    known_hazards: List[str] = field(default_factory=list)

@dataclass
class RouteSelectionState:
    current_node_id: str
    available_routes: List[RouteOption]
    selected_route_id: Optional[str] = None

    def select_route(self, route_id: str) -> bool:
        """Selects a route if it is available. Returns True if successful."""
        for route in self.available_routes:
            if route.route_id == route_id:
                self.selected_route_id = route_id
                return True
        return False

def calculate_route_hazards(route_type: str, floor_id: int, debug: bool = False):
    """Stub to calculate hazard profile for a given route type."""
    if route_type == "stable_primary":
        return {"combat_hazard": 0.2, "mutation_hazard": 0.1, "drain_hazard": 0.1}
    elif route_type == "unstable_alpha":
        return {"combat_hazard": 0.6, "mutation_hazard": 0.8, "drain_hazard": 0.4}
    elif route_type == "scarred_corridor":
        return {"combat_hazard": 0.4, "mutation_hazard": 0.5, "drain_hazard": 0.9}
    else:
        return {"combat_hazard": 0.3, "mutation_hazard": 0.3, "drain_hazard": 0.3}

def make_manual_route_selection(floor_id: int, selected_route_id: str, available_route_ids: list, strategic_bias: str = "DEFAULT", debug: bool = False):
    """Stub to simulate an artifact generated when a player manually selects a route."""
    return {
        "ok": True,
        "selection": {
            "selected_route_id": selected_route_id,
            "available_routes": available_route_ids,
            "strategic_bias": strategic_bias,
            "hazard_profile": {"combat_hazard": 0.3, "mutation_hazard": 0.3}
        }
    }
