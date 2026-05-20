from dataclasses import dataclass, field
from typing import List

@dataclass
class RouteVisibilitySnapshot:
    route_id: str
    visibility_level: str
    environmental_cues: List[str] = field(default_factory=list)
    confirmed_hazards: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.visibility_level not in ["none", "low", "medium", "high"]:
            raise ValueError(f"Invalid visibility level: {self.visibility_level}")

def calculate_route_visibility(route: dict, claims: list, current_floor: int, debug: bool = False):
    """Stub to calculate hazard visibility for a route based on domain claims."""
    # route_visibility_must_be_partial_not_perfect_information: true
    accuracy = 0.5
    if claims:
        accuracy = 0.8 # Boosted accuracy but not 1.0
    
    hazard_profile = route.get("hazard_profile", {"combat_hazard": 0.3, "mutation_hazard": 0.3, "drain_hazard": 0.3})
    
    # Partial perceived hazards
    perceived_hazards = {
        "combat": hazard_profile.get("combat_hazard", 0.0) * accuracy,
        "mutation": hazard_profile.get("mutation_hazard", 0.0) * accuracy,
        "drain": hazard_profile.get("drain_hazard", 0.0) * accuracy,
    }
    
    visibility_band = "CLEAR" if accuracy > 0.6 else "VAGUE"
    
    return {
        "visibility_band": visibility_band,
        "information_accuracy": accuracy,
        "perceived_hazards": perceived_hazards
    }
