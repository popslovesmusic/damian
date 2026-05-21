import json

class AnimationManager:
    def __init__(self, contract_path, state_path, sheet_rules_path, enemy_profile_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(state_path, 'r') as f:
            self.state_profile = json.load(f)
        with open(sheet_rules_path, 'r') as f:
            self.sheet_rules = json.load(f)
        with open(enemy_profile_path, 'r') as f:
            self.enemy_profile = json.load(f)

    def get_animation_state(self, entity_type, entity_state):
        """Maps runtime state to animation identifier."""
        # Simplified mapping logic for prototype
        if entity_type == "player":
            if entity_state.get("health", 100) <= 0:
                return self.state_profile["player"]["death"]
            return self.state_profile["player"].get("idle")
            
        if entity_type == "enemy":
            if entity_state.get("hunt_state") == "HUNTING":
                return self.state_profile["enemy"]["hunting"]
            return self.state_profile["enemy"].get("idle")
            
        return self.contract["default_fallback"]
