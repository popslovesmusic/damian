import json
import random

class RoomDressingManager:
    def __init__(self, contract_path, placement_path, clutter_path, silhouette_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(placement_path, 'r') as f:
            self.placement_rules = json.load(f)
        with open(clutter_path, 'r') as f:
            self.clutter_profile = json.load(f)
        with open(silhouette_path, 'r') as f:
            self.silhouette_profile = json.load(f)

    def dress_room(self, room_data):
        """Adds prop placement metadata to room_data."""
        room_type = room_data.get("room_type", "default")
        
        props = []
        if room_type in self.clutter_profile:
            # Place some props
            candidates = self.clutter_profile[room_type]
            num_props = random.randint(1, self.contract.get("max_props_per_room", 5))
            props = random.sample(candidates, min(len(candidates), num_props))
            
        room_data["props"] = props
        return room_data
