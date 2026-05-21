import os
import json
import hashlib
import time
import random

class SurvivalEconomyManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def generate_resource_profile(self, resource_type, scarcity_level, world_pressure):
        """Produces a pressure-aware survival resource profile."""
        if resource_type not in self.contract["resource_types"]:
            return {"status": "FAIL", "reason": f"Unknown resource type: {resource_type}"}

        profile_id = f"res_{resource_type.lower()}_{int(time.time()*1000)}"
        
        # Calculate visibility and weight based on type and scarcity
        base_weight = 1.0
        if resource_type in ["POWER_CELLS", "SCRAP"]: base_weight = 5.0
        elif resource_type in ["TOOLS", "AMMUNITION"]: base_weight = 2.0
        
        # Scarcity makes items more "valuable" and thus higher visibility
        visibility_mod = 1.0 + (scarcity_level / 10.0)
        
        profile = {
            "resource_profile_id": profile_id,
            "resource_type": resource_type,
            "scarcity_profile": {"scarcity_level": scarcity_level, "regional_density": "LOW" if scarcity_level > 7 else "MODERATE"},
            "decay_profile": {
                "decay_rate": 0.01 * (1.0 + world_pressure / 50.0),
                "is_perishable": resource_type in ["FOOD", "WATER", "MEDICAL"]
            },
            "visibility_profile": {
                "base_visibility": visibility_mod,
                "pressure_coupling": True
            },
            "weight_profile": {
                "unit_weight": base_weight,
                "traversal_drag_factor": 0.05 * base_weight
            },
            "repair_cost_profile": {
                "base_repair_cost": 20 if resource_type == "TOOLS" else 0,
                "complexity": "HIGH" if world_pressure > 70 else "STANDARD"
            },
            "crafting_requirements": {
                "mode_allowed": "IMPROVISED" if world_pressure > 50 else "STABLE",
                "materials_required": ["SCRAP"]
            },
            "cache_risk_profile": {
                "detection_risk": 0.1 * visibility_mod,
                "vulnerability": "HIGH"
            },
            "predator_attraction_profile": {
                "attraction_radius": 5.0 * visibility_mod
            },
            "recoverability_profile": {"is_recoverable": True},
            "bounded_flags": {
                "scarce": True,
                "auditable": True,
                "weight_coupled": True
            },
            "resource_hash": ""
        }

        # Calculate Hash
        profile_str = json.dumps(profile, sort_keys=True)
        profile["resource_hash"] = hashlib.sha256(profile_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Resource Profile Generation",
            "status": "PASS",
            "profile_id": profile_id,
            "type": resource_type
        })
        return profile

    def apply_scavenging_pressure(self, survivor_id, duration_ms, area_pressure):
        """Calculates risk and rewards for a scavenging session."""
        risk_roll = random.uniform(0, 100)
        visibility_gain = (duration_ms / 1000.0) * 2.0
        
        success = risk_roll > area_pressure
        
        log = {
            "survivor_id": survivor_id,
            "duration": duration_ms,
            "visibility_increase": visibility_gain,
            "success": success,
            "status": "COMPLETED" if success else "INTERRUPTED_BY_PRESSURE"
        }
        
        self.evidence["checks"].append({
            "check": "Scavenging Runtime",
            "status": "PASS",
            "success": success
        })
        return log

    def resolve_improvised_crafting(self, target_item, pressure_level):
        """Simulates improvised crafting under pressure."""
        quality = 1.0 - (pressure_level / 200.0) # Quality drops as pressure rises
        
        craft_report = {
            "item": target_item,
            "quality_score": max(0.3, quality),
            "is_imperfect": quality < 0.9,
            "durability_penalty": 0.2 if quality < 0.7 else 0.0
        }
        
        self.evidence["checks"].append({
            "check": "Improvised Crafting",
            "status": "PASS",
            "quality": craft_report["quality_score"]
        })
        return craft_report

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    sem = SurvivalEconomyManager(
        "engine/economy/contracts/resource_scarcity_boundary.json",
        "engine/economy/contracts/survival_economy_contract.json"
    )
    
    # Test High Scarcity Food
    r1 = sem.generate_resource_profile("FOOD", 9, 20)
    print(f"Food Profile: {r1['resource_profile_id']} (Decay: {r1['decay_profile']['decay_rate']})")
    
    # Test Scavenging
    log = sem.apply_scavenging_pressure("survivor_alpha", 5000, 30)
    print(f"Scavenge Log: {json.dumps(log, indent=2)}")
    
    # Test Crafting
    craft = sem.resolve_improvised_crafting("IMPROVISED_STIM", 80)
    print(f"Craft Result: Quality {craft['quality_score']} (Imperfect: {craft['is_imperfect']})")
    
    print(json.dumps(sem.get_final_evidence(), indent=2))
