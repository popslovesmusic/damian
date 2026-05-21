import json

class HazardContactManager:
    def __init__(self, contract_path, rules_path, damage_path, warning_path, boundary_manager):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)
        with open(damage_path, 'r') as f:
            self.damage_profile = json.load(f)
        with open(warning_path, 'r') as f:
            self.warning_profile = json.load(f)
        self.boundary_manager = boundary_manager

    def resolve_hazard(self, room_id, position):
        """Checks for hazard contact and returns effect."""
        contact = self.boundary_manager.check_contact(room_id, position)
        
        if contact and contact.get("type") == "hazard":
            hazard_type = contact.get("data", {}).get("type", "corruption")
            hazard_rules = self.rules.get(hazard_type, {"damage": 1, "pressure": 1})
            return {
                "damage": hazard_rules.get("damage", 0),
                "pressure": hazard_rules.get("pressure", 0),
                "event": f"HAZARD_CONTACT_{hazard_type.upper()}"
            }
        return None
