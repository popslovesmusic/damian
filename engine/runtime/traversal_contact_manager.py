import json

class TraversalContactManager:
    def __init__(self, contract_path, movement_rules_path, stamina_path, route_path, boundary_manager):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(movement_rules_path, 'r') as f:
            self.movement_rules = json.load(f)
        with open(stamina_path, 'r') as f:
            self.stamina_profile = json.load(f)
        with open(route_path, 'r') as f:
            self.route_profile = json.load(f)
        self.boundary_manager = boundary_manager

    def resolve_movement(self, room_id, position, movement_type):
        """Resolves movement request against boundaries."""
        # Check collision
        contact = self.boundary_manager.check_contact(room_id, position)
        
        # If collision (solid), movement is blocked
        if contact and contact.get("data", {}).get("solid"):
            return {"status": "BLOCKED", "resolved_position": None}
            
        # Otherwise, resolve movement based on type
        rules = self.movement_rules.get(movement_type, self.movement_rules["walk"])
        return {"status": "MOVED", "resolved_position": position, "meta": rules}
