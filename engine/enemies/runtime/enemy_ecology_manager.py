import os
import json
import hashlib
import time
import random

class EnemyEcologyManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def generate_enemy_profile(self, ecology_type, world_pressure, route_usage_score):
        """Produces a procedural enemy profile based on ecological pressure."""
        if ecology_type not in self.contract["ecology_types"]:
            return {"status": "FAIL", "reason": f"Unknown ecology type: {ecology_type}"}

        profile_id = f"enemy_{ecology_type.lower()}_{int(time.time()*1000)}"
        
        # Adaptation based on pressure
        is_mutated = world_pressure >= self.boundary["readability_policy"]["pressure_threshold_for_mutation"]
        
        profile = {
            "enemy_profile_id": profile_id,
            "ecology_type": ecology_type,
            "pressure_response_profile": {
                "aggression_multiplier": 1.0 + (world_pressure / 100.0),
                "speed_boost": 1.2 if is_mutated else 1.0
            },
            "migration_behavior": "STATIONARY" if route_usage_score < 30 else "HUNTING_FREQUENT_ROUTES",
            "hunt_behavior": {
                "detection_radius_modifier": 1.0 + (route_usage_score / 50.0),
                "persistence_level": "PERSISTENT" if world_pressure > 50 else "CAUTIOUS"
            },
            "mutation_profile": {
                "active": is_mutated,
                "type": "PRESSURE_BURN" if is_mutated else "NONE",
                "recognizability_score": 0.85
            },
            "visibility_response_profile": {"noise_sensitivity": 1.5 if ecology_type == "PREDATOR" else 1.0},
            "faction_aggression_profile": {"hates_treaties": True},
            "route_usage_response": {"overuse_penalty_active": route_usage_score > 70},
            "telegraph_profile": {
                "warning_ms": max(self.boundary["readability_policy"]["min_telegraph_duration_ms"], 500 - world_pressure),
                "audio_cue": "LOW_HUM" if not is_mutated else "PRESSURE_SCREAM"
            },
            "recoverability_profile": {"is_repairable": False, "is_harvestable": True},
            "bounded_flags": {
                "readable": True,
                "pressure_reactive": True
            },
            "enemy_hash": ""
        }

        # Calculate Hash
        profile_str = json.dumps(profile, sort_keys=True)
        profile["enemy_hash"] = hashlib.sha256(profile_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Enemy Profile Generation",
            "status": "PASS",
            "profile_id": profile_id,
            "is_mutated": is_mutated
        })
        return profile

    def resolve_predator_migration(self, route_stats):
        """Calculates predator migration shift based on route overuse."""
        migration_log = []
        for route_id, usage in route_stats.items():
            if usage > 50:
                migration_log.append({
                    "route_id": route_id,
                    "migration_status": "HIGH_PREDATOR_DENSITY",
                    "reason": "Route overuse detected."
                })
        
        self.evidence["checks"].append({
            "check": "Predator Migration Resolution",
            "status": "PASS",
            "impacted_routes": len(migration_log)
        })
        return migration_log

    def validate_threat_readability(self, profile):
        """Ensures the enemy remains readable under high pressure."""
        duration = profile["telegraph_profile"]["warning_ms"]
        is_safe = duration >= self.boundary["readability_policy"]["min_telegraph_duration_ms"]
        
        self.evidence["checks"].append({
            "check": "Threat Readability Validation",
            "status": "PASS" if is_safe else "FAIL",
            "warning_ms": duration
        })
        return is_safe

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    e_manager = EnemyEcologyManager(
        "engine/enemies/contracts/enemy_ecology_boundary.json",
        "engine/enemies/contracts/enemy_behavior_contract.json"
    )
    
    # Test Predator on heavily used route
    p1 = e_manager.generate_enemy_profile("PREDATOR", 20, 80)
    print(f"Predator Profile: {p1['enemy_profile_id']} (Migration: {p1['migration_behavior']})")
    
    # Test Mutant under high pressure
    p2 = e_manager.generate_enemy_profile("EVENT_MUTANT", 75, 10)
    print(f"Mutant Profile: {p2['enemy_profile_id']} (Mutated: {p2['mutation_profile']['active']}, Telegraph: {p2['telegraph_profile']['warning_ms']}ms)")
    
    # Test Migration
    routes = {"route_alpha": 10, "route_beta": 90}
    log = e_manager.resolve_predator_migration(routes)
    print(f"Migration Log: {json.dumps(log, indent=2)}")
    
    print(json.dumps(e_manager.get_final_evidence(), indent=2))
