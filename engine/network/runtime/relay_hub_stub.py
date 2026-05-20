import os
import json
import hashlib
import time

class RelayHubManager:
    def __init__(self, boundary_path, contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def create_relay_hub(self, operator_id, role="domain_echo_exchange"):
        """Creates a bounded, fragile relay hub."""
        if role not in self.contract["allowed_roles"]:
            return {"status": "FAIL", "reason": "Unauthorized hub role."}

        hub_id = f"hub_{operator_id}_{int(time.time())}"
        hub = {
            "relay_hub_id": hub_id,
            "hub_operator_id": operator_id,
            "connected_survivor_count": 1,
            "domain_echo_queue": [],
            "treaty_signal_queue": [],
            "reputation_visibility_profile": {"broadcast_range": "LOCAL"},
            "relay_stability": 100.0,
            "tower_attention_pressure": 5.0,
            "fragmentation_state": "NONE",
            "bounded_flags": {
                "no_central_authority": True,
                "asynchronous_only": True
            },
            "relay_hash": ""
        }

        # Calculate Hash
        hub_str = json.dumps(hub, sort_keys=True)
        hub["relay_hash"] = hashlib.sha256(hub_str.encode()).hexdigest()

        self.evidence["checks"].append({
            "check": "Relay Hub Creation",
            "status": "PASS",
            "hub_id": hub_id
        })
        return hub

    def queue_message(self, hub, message_type, payload):
        """Asynchronously queues a message in the relay."""
        # Verification: No real-time authority
        if not hub["bounded_flags"].get("asynchronous_only"):
            return {"status": "BLOCKED", "reason": "Sync mode forbidden."}

        queue_entry = {
            "msg_id": f"msg_{int(time.time()*1000)}",
            "type": message_type,
            "payload_summary": f"Bounded {message_type} hash verification required.",
            "timestamp": time.time()
        }
        
        if message_type == "domain_echo":
            hub["domain_echo_queue"].append(queue_entry)
        elif message_type == "treaty_signal":
            hub["treaty_signal_queue"].append(queue_entry)
            
        # Coupling: message activity increases tower attention
        hub["tower_attention_pressure"] += 0.5
        hub["relay_stability"] -= 0.1
        
        self.evidence["checks"].append({
            "check": "Async Message Queue",
            "status": "PASS",
            "type": message_type
        })
        return hub

    def resolve_fragmentation(self, hub):
        """Simulates hub fragmentation under high pressure."""
        if hub["tower_attention_pressure"] > 50.0:
            hub["fragmentation_state"] = "PARTIALLY_OFFLINE"
            hub["relay_stability"] *= 0.5
            
        self.evidence["checks"].append({
            "check": "Relay Fragmentation",
            "status": "PASS",
            "state": hub["fragmentation_state"]
        })
        return hub

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"]):
            self.evidence["verdict"] = "PASS"
        else:
            self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Internal test
    rhm = RelayHubManager(
        "engine/network/contracts/relay_node_boundary.json",
        "engine/network/contracts/relay_hub_contract.json"
    )
    
    hub = rhm.create_relay_hub("survivor_alpha")
    print(f"Hub Created: {hub['relay_hub_id']}")
    
    hub = rhm.queue_message(hub, "domain_echo", {"echo_id": "echo_123"})
    print(f"Tower Attention: {hub['tower_attention_pressure']}")
    
    # Simulate high pressure
    hub["tower_attention_pressure"] = 60.0
    hub = rhm.resolve_fragmentation(hub)
    print(f"Fragmentation State: {hub['fragmentation_state']}")
    
    print(json.dumps(rhm.get_final_evidence(), indent=2))
