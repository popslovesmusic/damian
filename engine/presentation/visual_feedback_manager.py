import json

class VisualFeedbackManager:
    def __init__(self, contract_path, interaction_path, hazard_path, residue_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(interaction_path, 'r') as f:
            self.interaction_rules = json.load(f)
        with open(hazard_path, 'r') as f:
            self.hazard_rules = json.load(f)
        with open(residue_path, 'r') as f:
            self.residue_rules = json.load(f)

    def generate_feedback(self, game_state):
        feedback = {
            "layers": {}
        }
        
        # Example feedback generation
        if game_state.get("enemy_hunt_state") == "HUNTING":
            feedback["layers"]["enemy_hunt"] = "hunted_vignette"
            
        if game_state.get("pressure", 0) > 60:
            feedback["layers"]["pressure"] = "dark_zone"
            
        return feedback
