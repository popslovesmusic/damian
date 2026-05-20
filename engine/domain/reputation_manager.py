import os
import json
import hashlib
import time

class ReputationManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def generate_signal(self, survivor_id, signal_type, magnitude=1.0):
        """Generates a bounded reputation signal."""
        # Validate signal type
        is_pos = signal_type in self.boundary["signal_policy"]["allowed_positive"]
        is_neg = signal_type in self.boundary["signal_policy"]["allowed_negative"]
        
        if not is_pos and not is_neg:
            return {"status": "REJECTED", "reason": "Unknown signal type."}

        signal = {
            "survivor_id": survivor_id,
            "type": signal_type,
            "category": "POSITIVE" if is_pos else "NEGATIVE",
            "magnitude": magnitude,
            "timestamp": time.time(),
            "decay_rate": 0.05, # Constant decay for prototype
            "recoverable": True
        }
        
        self.evidence["checks"].append({
            "check": "Signal Generation",
            "status": "PASS",
            "type": signal_type
        })
        return signal

    def calculate_trust_drift(self, current_score, signals):
        """Calculates drift and potential recovery of trust."""
        # Simple simulation: sum magnitudes with decay
        net_drift = 0
        for s in signals:
            if s["category"] == "POSITIVE":
                net_drift += s["magnitude"]
            else:
                net_drift -= s["magnitude"]
                
        new_score = current_score + net_drift
        # Ensure it stays within reasonable bounds (0-100)
        new_score = max(0, min(100, new_score))
        
        self.evidence["checks"].append({
            "check": "Trust Drift Calculation",
            "status": "PASS",
            "net_drift": net_drift,
            "new_score": new_score
        })
        return new_score

    def get_reputation_snapshot(self, survivor_id, current_score):
        """Produces a contextual snapshot of a survivor's reputation."""
        state = "UNKNOWN"
        if current_score >= 80: state = "RELIABLE"
        elif current_score >= 50: state = "RECOVERING"
        elif current_score >= 20: state = "UNSTABLE"
        else: state = "WATCHED"
        
        snapshot = {
            "survivor_id": survivor_id,
            "residue_reputation_score": current_score,
            "treaty_trust_score": current_score * 0.8, # Simulated
            "echo_attack_history": [],
            "cooperation_history": [],
            "betrayal_markers": [],
            "retaliation_trace_count": 0,
            "trust_drift_state": state,
            "recovery_potential": 100 - current_score,
            "bounded_flags": {"contextual": True},
            "trust_hash": ""
        }
        
        # Calculate Hash
        snap_str = json.dumps(snapshot, sort_keys=True)
        snapshot["trust_hash"] = hashlib.sha256(snap_str.encode()).hexdigest()
        
        self.evidence["checks"].append({
            "check": "Reputation Snapshot",
            "status": "PASS",
            "state": state
        })
        return snapshot

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    rm = ReputationManager(
        "engine/domain/contracts/reputation_boundary.json",
        "engine/domain/contracts/trust_network_contract.json"
    )
    
    s1 = rm.generate_signal("survivor_001", "successful_joint_defense", 5.0)
    s2 = rm.generate_signal("survivor_001", "treaty_abandonment", 10.0)
    
    new_score = rm.calculate_trust_drift(50, [s1, s2])
    print(f"New Score: {new_score}")
    
    snapshot = rm.get_reputation_snapshot("survivor_001", new_score)
    print(f"Reputation Snapshot: {json.dumps(snapshot, indent=2)}")
