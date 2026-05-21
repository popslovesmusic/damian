import json
import random

class LandmarkStorytellingManager:
    def __init__(self, contract_path, generation_path, story_path, faction_path, ritual_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(generation_path, 'r') as f:
            self.generation_rules = json.load(f)
        with open(story_path, 'r') as f:
            self.story_profile = json.load(f)
        with open(faction_path, 'r') as f:
            self.faction_profile = json.load(f)
        with open(ritual_path, 'r') as f:
            self.ritual_profile = json.load(f)

    def generate_landmark_for_room(self, room_data, world_memory):
        """Generates landmark data for a given room."""
        if random.random() > self.generation_rules.get("generation_chance", 0.3):
            return None
            
        landmark_type = random.choice(self.contract["active_landmark_types"])
        
        landmark_data = {
            "landmark_id": f"L_{room_data['room_id']}_{random.randint(1000, 9999)}",
            "type": landmark_type,
            "components": {}
        }
        
        if landmark_type == "historical":
            landmark_data["components"] = self.story_profile
        elif landmark_type == "faction":
            landmark_data["components"] = self.faction_profile
        elif landmark_type == "ritual":
            landmark_data["components"] = self.ritual_profile
            
        return landmark_data
