import json

class LightingManager:
    def __init__(self, contract_path, fog_path, occlusion_path, danger_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(fog_path, 'r') as f:
            self.fog_profile = json.load(f)
        with open(occlusion_path, 'r') as f:
            self.occlusion_rules = json.load(f)
        with open(danger_path, 'r') as f:
            self.danger_profile = json.load(f)

    def get_render_parameters(self, game_state):
        """Maps runtime state to lighting, fog, and occlusion parameters."""
        pressure = game_state.get("pressure", 0)
        hunt_state = game_state.get("enemy_hunt_state", "UNKNOWN")
        
        params = {
            "brightness": self.contract["default_ambient"],
            "fog_density": self.fog_profile["clear"],
            "occlusion": self.occlusion_rules,
            "flicker": False
        }
        
        # Apply pressure-based logic
        if pressure > 70:
            params["brightness"] = 0.4
            params["fog_density"] = self.fog_profile["pressure_fog"]
            
        # Apply hunt-based danger
        if hunt_state == "HUNTING":
            danger = self.danger_profile["hunted"]
            params["brightness"] = danger["brightness"]
            params["flicker"] = danger["flicker"]
            
        return params
