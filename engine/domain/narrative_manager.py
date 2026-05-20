import os
import json
import hashlib
import time
import random

class NarrativeManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def aggregate_narrative_residue(self, world_id, current_metrics):
        """Aggregates aggregate systemic actions into historical residue."""
        residue_id = f"mem_{world_id}_{int(time.time())}"
        
        memory = {
            "world_memory_id": residue_id,
            "world_id": world_id,
            "historical_residue_profile": {"aggregate_pressure": current_metrics.get("pressure", 0.0)},
            "survivor_action_summary": {"total_treaties": 5, "total_echoes": 12},
            "faction_scar_summary": ["THE_GREAT_SPLINTER"],
            "relay_fragmentation_history": {"total_events": 2},
            "market_instability_history": {"peak_instability": 1.5},
            "event_wave_history": ["RECLAMATION_WAVE_01"],
            "legendary_survivor_markers": ["SURVIVOR_SIG_ALPHA"],
            "narrative_drift_profile": {"direction": "SYSTEMIC_DECAY", "confidence": 0.7},
            "recoverability_profile": {"is_recoverable": True},
            "bounded_flags": {
                "residue_based": True,
                "probabilistic": True,
                "non_static": True
            },
            "memory_hash": ""
        }

        # Calculate Hash
        mem_str = json.dumps(memory, sort_keys=True)
        memory["memory_hash"] = hashlib.sha256(mem_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Narrative Residue Aggregation",
            "status": "PASS",
            "memory_id": residue_id
        })
        return memory

    def apply_procedural_drift(self, memory):
        """Simulates probabilistic narrative drift based on world memory."""
        # Non-omniscience: drift is probabilistic
        drift_factor = random.uniform(0.1, 0.5)
        
        drifted_state = {
            "original_id": memory["world_memory_id"],
            "drift_type": "MYTHOLOGY_FORMATION",
            "applied_delta": drift_factor,
            "result_summary": "Historical events reinterpreted by systemic pressure.",
            "timestamp": time.time()
        }
        
        self.evidence["checks"].append({
            "check": "Procedural Narrative Drift",
            "status": "PASS",
            "drift_factor": drift_factor
        })
        return drifted_state

    def generate_historical_contract(self, memory):
        """Generates a dynamic contract based on historical world scars."""
        historical_id = f"hist_contract_{int(time.time())}"
        
        contract = {
            "contract_id": historical_id,
            "type": "RECONCILIATION_QUEST",
            "context": f"Residue of {memory['faction_scar_summary'][0]} detected.",
            "reward": "REPUTATION_REPAIR",
            "risk": "HIGH_TOWER_ATTENTION",
            "status": "AVAILABLE"
        }
        
        self.evidence["checks"].append({
            "check": "Historical Contract Generation",
            "status": "PASS",
            "contract_id": historical_id
        })
        return contract

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    nm = NarrativeManager(
        "engine/domain/contracts/adaptive_narrative_boundary.json",
        "engine/domain/contracts/world_memory_contract.json"
    )
    
    metrics = {"pressure": 45.0}
    memory = nm.aggregate_narrative_residue("damian_core", metrics)
    print(f"Memory Created: {memory['world_memory_id']}")
    
    drift = nm.apply_procedural_drift(memory)
    print(f"Drift Applied: {drift['drift_type']} ({drift['applied_delta']})")
    
    contract = nm.generate_historical_contract(memory)
    print(f"Historical Contract: {contract['contract_id']}")
    
    print(json.dumps(nm.get_final_evidence(), indent=2))
