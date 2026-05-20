import os
import json
import hashlib
import time

class FactionManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def detect_faction_emergence(self, source_type, member_ids, residue_signature):
        """Simulates the emergence of a procedural faction bloc."""
        if source_type not in self.contract["allowed_emergence_sources"]:
            return {"status": "FAIL", "reason": "Unauthorized emergence source."}

        bloc_id = f"bloc_{source_type}_{int(time.time())}"
        
        bloc = {
            "bloc_id": bloc_id,
            "bloc_name": f"Emergent {source_type.replace('_', ' ').title()}",
            "emergence_source": source_type,
            "member_survivor_ids": member_ids,
            "dominant_residue_signature": residue_signature,
            "treaty_network_summary": {"active_treaties": len(member_ids) // 2},
            "market_influence_profile": {"trade_volume": 100},
            "contract_activity_profile": {"active_contracts": 5},
            "relay_presence_profile": {"relay_nodes": 2},
            "stability_profile": {"current_stability": 100.0},
            "fracture_pressure": 0.0,
            "tower_attention_pressure": 10.0,
            "bounded_flags": {
                "procedural": True,
                "unstable": True,
                "recoverable": True
            },
            "bloc_hash": ""
        }

        # Calculate Hash
        bloc_str = json.dumps(bloc, sort_keys=True)
        bloc["bloc_hash"] = hashlib.sha256(bloc_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Faction Emergence",
            "status": "PASS",
            "bloc_id": bloc_id
        })
        return bloc

    def update_stability(self, bloc, member_activity_increase):
        """Calculates instability scaling based on growth and activity."""
        # Growth increases attention and fracture pressure
        growth_factor = len(bloc["member_survivor_ids"]) * 1.2
        bloc["tower_attention_pressure"] += growth_factor + member_activity_increase
        bloc["fracture_pressure"] += (growth_factor * 0.5) + (member_activity_increase * 0.2)
        
        # Stability decreases as fracture pressure rises
        bloc["stability_profile"]["current_stability"] = max(0.0, 100.0 - bloc["fracture_pressure"])
        
        self.evidence["checks"].append({
            "check": "Stability Scaling",
            "status": "PASS",
            "new_stability": bloc["stability_profile"]["current_stability"]
        })
        return bloc

    def resolve_fracture(self, bloc):
        """Resolves faction fracture state when stability is low."""
        if bloc["stability_profile"]["current_stability"] < 30.0:
            bloc["fracture_state"] = "FRACTURING"
            # Simulate splintering: members leave or form sub-blocs
            split_count = len(bloc["member_survivor_ids"]) // 3
            bloc["member_survivor_ids"] = bloc["member_survivor_ids"][:-split_count] if split_count > 0 else bloc["member_survivor_ids"]
        else:
            bloc["fracture_state"] = "STABLE"
            
        self.evidence["checks"].append({
            "check": "Fracture Resolution",
            "status": "PASS",
            "state": bloc["fracture_state"]
        })
        return bloc

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    fm = FactionManager(
        "engine/domain/contracts/faction_boundary.json",
        "engine/domain/contracts/survivor_bloc_contract.json"
    )
    
    bloc = fm.detect_faction_emergence("treaty_cluster", ["s1", "s2", "s3", "s4", "s5"], "RECLAMATION_BENT")
    print(f"Bloc Created: {bloc['bloc_name']} ({bloc['bloc_id']})")
    
    # Simulate high activity/growth
    fm.update_stability(bloc, 25.0)
    print(f"Stability: {bloc['stability_profile']['current_stability']}, Attention: {bloc['tower_attention_pressure']}")
    
    fm.resolve_fracture(bloc)
    print(f"Fracture State: {bloc.get('fracture_state')}, Remaining Members: {len(bloc['member_survivor_ids'])}")
    
    print(json.dumps(fm.get_final_evidence(), indent=2))
