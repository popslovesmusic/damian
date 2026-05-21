import json

class InteractionObjectManager:
    def __init__(self, contract_path, rules_path, profile_path, prompt_path, boundary_manager):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)
        with open(profile_path, 'r') as f:
            self.profile = json.load(f)
        with open(prompt_path, 'r') as f:
            self.prompt_rules = json.load(f)
        self.boundary_manager = boundary_manager

    def can_interact(self, room_id, position):
        """Checks if interaction is possible at position."""
        contact = self.boundary_manager.check_contact(room_id, position)
        if contact and contact.get("type") == "interaction":
            object_id = contact.get("data", {}).get("object_id")
            # Lookup object in profile
            for obj in self.profile.values():
                if obj["id"] == object_id:
                    return {"can_interact": True, "object_type": obj["type"]}
        return {"can_interact": False, "object_type": None}
