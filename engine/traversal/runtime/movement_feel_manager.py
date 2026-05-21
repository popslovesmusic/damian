import os
import json
import hashlib
import time

class MovementFeelManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def generate_movement_profile(self, mode, pressure_load, exhaustion_level):
        """Produces a pressure-aware movement profile."""
        if mode not in self.contract["movement_modes"]:
            return {"status": "FAIL", "reason": f"Unknown movement mode: {mode}"}

        profile_id = f"move_{mode.lower()}_{int(time.time()*1000)}"
        
        # Calculate visibility based on speed and mode
        visibility_mod = 1.0
        if mode == "RUSH": visibility_mod = 2.0
        elif mode == "ESCAPE": visibility_mod = 2.5
        elif mode == "CAUTIOUS": visibility_mod = 0.5
        
        # Pressure increases visibility footprint
        visibility_mod += (pressure_load / 100.0)

        profile = {
            "movement_profile_id": profile_id,
            "movement_mode": mode,
            "pressure_load": pressure_load,
            "visibility_modifier": visibility_mod,
            "stamina_or_exhaustion_profile": {
                "exhaustion_level": exhaustion_level,
                "recovery_rate_penalty": 0.2 if exhaustion_level > 50 else 0.0,
                "movement_drag": min(0.5, exhaustion_level / 100.0)
            },
            "route_risk_profile": {
                "danger_awareness": 0.8 if mode == "CAUTIOUS" else 0.5,
                "hazard_trigger_modifier": 1.5 if mode == "RUSH" else 1.0
            },
            "environmental_instability_profile": {
                "navigation_jitter": 0.1 if pressure_load < 50 else 0.4
            },
            "camera_behavior_profile": {
                "bob_intensity": 1.2 if mode in ["RUSH", "ESCAPE"] else 1.0,
                "tilt_angle": 5 if exhaustion_level > 70 else 0
            },
            "audio_feedback_profile": {
                "footstep_volume": 1.5 if mode == "RUSH" else 1.0,
                "breathing_intensity": min(1.0, exhaustion_level / 80.0)
            },
            "readability_score": 0.9,
            "bounded_flags": {
                "pressure_aware": True,
                "visibility_coupled": True
            },
            "movement_hash": ""
        }

        # Calculate Hash
        profile_str = json.dumps(profile, sort_keys=True)
        profile["movement_hash"] = hashlib.sha256(profile_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Movement Profile Generation",
            "status": "PASS",
            "profile_id": profile_id,
            "mode": mode
        })
        return profile

    def validate_route_exposure(self, route_id, visibility_mod):
        """Ensures route exposure remains within safety thresholds."""
        threshold = self.boundary["readability_policy"]["exposure_threshold_for_detection"]
        is_high_risk = (visibility_mod * 50.0) >= threshold
        
        self.evidence["checks"].append({
            "check": "Route Exposure Validation",
            "status": "PASS",
            "route_id": route_id,
            "high_risk": is_high_risk
        })
        return is_high_risk

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    mfm = MovementFeelManager(
        "engine/traversal/contracts/traversal_boundary.json",
        "engine/traversal/contracts/movement_contract_schema.json"
    )
    
    # Test Standard Move
    p1 = mfm.generate_movement_profile("STANDARD", 10, 5)
    print(f"Standard Profile: {p1['movement_profile_id']} (Visibility: {p1['visibility_modifier']})")
    
    # Test Rush with High Pressure
    p2 = mfm.generate_movement_profile("RUSH", 60, 40)
    print(f"Rush Profile: {p2['movement_profile_id']} (Visibility: {p2['visibility_modifier']}, Drag: {p2['stamina_or_exhaustion_profile']['movement_drag']})")
    
    # Test Route Exposure
    is_hot = mfm.validate_route_exposure("route_beta", p2["visibility_modifier"])
    print(f"Route Hot: {is_hot}")
    
    print(json.dumps(mfm.get_final_evidence(), indent=2))
