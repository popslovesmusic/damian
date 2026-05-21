import json

class RoomIdentityAuditor:
    def __init__(self, contract_path, readability_path, profile_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(readability_path, 'r') as f:
            self.readability_rules = json.load(f)
        with open(profile_path, 'r') as f:
            self.score_profile = json.load(f)

    def audit_room(self, room_data):
        """Scores a room's visual identity."""
        room_type = room_data.get("room_type", "default")
        props = room_data.get("props", [])
        
        if room_type not in self.score_profile:
            return {"score": 1.0, "status": "PASS"} # No rules for this type

        profile = self.score_profile[room_type]
        score = 0.0
        
        # Check props
        if len(props) >= profile.get("min_props", 0):
            score += 0.5
        
        required = profile.get("required_props", [])
        found_required = [p for p in props if p in required]
        if len(found_required) >= len(required):
            score += 0.5
        
        status = "PASS" if score >= self.contract.get("min_identity_score", 0.7) else "FAIL"
        return {"score": score, "status": status}
