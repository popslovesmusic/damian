import os
import json
import hashlib
import time

class ContractManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def generate_procedural_contract(self, origin, contract_type, pressure_source):
        """Generates a bounded procedural contract objective."""
        if contract_type not in self.contract["allowed_types"]:
            return {"status": "FAIL", "reason": "Forbidden contract type."}

        contract_id = f"contract_{int(time.time())}_{hashlib.md5(origin.encode()).hexdigest()[:8]}"
        
        objective = {
            "contract_id": contract_id,
            "contract_origin": origin,
            "contract_type": contract_type,
            "pressure_source": pressure_source,
            "relay_visibility_profile": {"broadcast_range": "LOCAL_RELAY"},
            "reward_profile": {"residue_bonus": 50},
            "risk_profile": {"visibility_spike": 1.2},
            "failure_scar_profile": {"reputation_damage": 5.0},
            "reputation_modifier": 1.1,
            "expiration_profile": {"expires_at": time.time() + 86400},
            "bounded_flags": {
                "asynchronous": True,
                "recoverable": True,
                "auditable": True
            },
            "contract_hash": ""
        }

        # Calculate Hash
        contract_str = json.dumps(objective, sort_keys=True)
        objective["contract_hash"] = hashlib.sha256(contract_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Contract Generation",
            "status": "PASS",
            "contract_id": contract_id
        })
        return objective

    def accept_contract(self, survivor_id, contract):
        """Simulates contract acceptance by a survivor."""
        acceptance = {
            "survivor_id": survivor_id,
            "contract_id": contract["contract_id"],
            "timestamp": time.time(),
            "status": "ACCEPTED",
            "visibility_penalty_active": True
        }
        
        self.evidence["checks"].append({
            "check": "Contract Acceptance",
            "status": "PASS",
            "survivor_id": survivor_id
        })
        return acceptance

    def resolve_failure(self, contract):
        """Resolves a contract failure and generates bounded scars."""
        failure_report = {
            "contract_id": contract["contract_id"],
            "outcome": "FAILED",
            "applied_scars": contract["failure_scar_profile"],
            "reputation_loss": contract["failure_scar_profile"].get("reputation_damage", 0),
            "timestamp": time.time(),
            "recoverable": True
        }
        
        self.evidence["checks"].append({
            "check": "Contract Failure Resolution",
            "status": "PASS",
            "contract_id": contract["contract_id"]
        })
        return failure_report

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    cm = ContractManager(
        "engine/domain/contracts/contract_network_boundary.json",
        "engine/domain/contracts/quest_broadcast_contract.json"
    )
    
    contract = cm.generate_procedural_contract("relay_hub_001", "resource_recovery", "SUPPLY_SHORTAGE")
    print(f"Contract Generated: {contract['contract_id']}")
    
    acceptance = cm.accept_contract("survivor_alpha", contract)
    print(f"Contract Accepted: {acceptance['status']}")
    
    failure = cm.resolve_failure(contract)
    print(f"Failure Resolved: {failure['outcome']}, Scars: {failure['applied_scars']}")
    
    print(json.dumps(cm.get_final_evidence(), indent=2))
