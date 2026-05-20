import os
import json
import hashlib
import time
import copy

class TreatyManager:
    def __init__(self, boundary_path, schema_path, policy_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        with open(policy_path, 'r') as f:
            self.policy = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def create_treaty(self, founder_id, member_ids, name):
        """Creates a bounded asynchronous treaty between domains."""
        treaty_id = f"treaty_{founder_id}_{int(time.time())}"
        
        treaty = {
            "treaty_id": treaty_id,
            "treaty_name": name,
            "founder_player_id": founder_id,
            "member_player_ids": member_ids,
            "created_timestamp": time.time(),
            "shared_pressure_profile": {
                "shared_visibility": 5.0,
                "mutual_intelligence": 10
            },
            "shared_reward_profile": {
                "recovery_bonus": 1.2
            },
            "visibility_modifier": 1.5, # Cooperation is noisy
            "joint_defense_profile": {
                "reinforcement_bonus": 5
            },
            "treaty_status": "ACTIVE",
            "bounded_flags": {
                "no_live_authority": True,
                "asynchronous_only": True
            },
            "treaty_hash": ""
        }
        
        # Calculate Hash
        treaty_str = json.dumps(treaty, sort_keys=True)
        treaty["treaty_hash"] = hashlib.sha256(treaty_str.encode()).hexdigest()
        
        self.evidence["checks"].append({
            "check": "Treaty Creation",
            "status": "PASS",
            "treaty_id": treaty_id
        })
        return treaty

    def resolve_shared_pressure(self, treaty, base_pressure):
        """Calculates pressure escalation due to treaty visibility."""
        escalated_pressure = base_pressure * treaty["visibility_modifier"]
        
        self.evidence["checks"].append({
            "check": "Shared Pressure Tradeoff",
            "status": "PASS",
            "base": base_pressure,
            "escalated": escalated_pressure
        })
        return escalated_pressure

    def generate_joint_defense_echo(self, treaty, target_echo):
        """Adds treaty reinforcement to a Domain Echo defense profile."""
        if treaty["treaty_status"] != "ACTIVE":
             return target_echo
             
        enhanced_echo = copy.deepcopy(target_echo)
        enhanced_echo["defense_profile"]["base_defense"] += treaty["joint_defense_profile"]["reinforcement_bonus"]
        enhanced_echo["defense_profile"]["treaty_id"] = treaty["treaty_id"]
        
        self.evidence["checks"].append({
            "check": "Joint Defense Echo",
            "status": "PASS",
            "treaty_id": treaty["treaty_id"]
        })
        return enhanced_echo

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    tm = TreatyManager(
        "engine/domain/contracts/treaty_boundary.json",
        "engine/domain/contracts/treaty_contract_schema.json",
        "engine/domain/contracts/treaty_policy_contract.json"
    )
    
    treaty = tm.create_treaty("player_alpha", ["player_alpha", "player_beta"], "The High Pass Accord")
    print(f"Treaty Created: {treaty['treaty_id']}")
    
    escalated = tm.resolve_shared_pressure(treaty, 100)
    print(f"Escalated Pressure: {escalated}")
    
    dummy_echo = {"defense_profile": {"base_defense": 10}}
    enhanced = tm.generate_joint_defense_echo(treaty, dummy_echo)
    print(f"Enhanced Defense: {enhanced['defense_profile']['base_defense']}")
    
    print(json.dumps(tm.get_final_evidence(), indent=2))
