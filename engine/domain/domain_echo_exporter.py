import os
import json
import hashlib
import time

class DomainEchoExporter:
    def __init__(self, contract_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)

    def export_echo(self, player_id, dashboard_snapshot):
        """Exports a Domain Echo snapshot from a dashboard snapshot."""
        echo_id = f"echo_{player_id}_{int(time.time())}"
        
        echo_snapshot = {
            "domain_echo_id": echo_id,
            "owner_player_id": player_id,
            "export_timestamp": time.time(),
            "source_dashboard_snapshot_id": dashboard_snapshot.get("snapshot_id", "unknown"),
            "domain_claim_summary": dashboard_snapshot.get("domain_claim_count", 0),
            "route_summary": "Simulated route topology",
            "residue_summary": dashboard_snapshot.get("total_residue", 0),
            "pressure_summary": dashboard_snapshot.get("environmental_pressure", 0),
            "scarring_summary": dashboard_snapshot.get("mutation_scars", 0),
            "reclamation_summary": 0,
            "defense_profile": {
                "base_defense": 10,
                "pressure_resistance": 5
            },
            "bounded_flags": {
                "read_only": True,
                "offline_adversarial": True
            },
            "sha256": ""
        }
        
        # Calculate Hash
        snapshot_str = json.dumps(echo_snapshot, sort_keys=True)
        echo_snapshot["sha256"] = hashlib.sha256(snapshot_str.encode()).hexdigest()
        
        return echo_snapshot

    def save_echo(self, snapshot, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{snapshot['domain_echo_id']}.json")
        with open(file_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        print(f"Domain Echo exported to {file_path}")
        return file_path

if __name__ == "__main__":
    # Internal test
    exporter = DomainEchoExporter("engine/domain/contracts/domain_echo_snapshot_contract.json")
    dummy_dash = {"snapshot_id": "dash_001", "domain_claim_count": 5, "total_residue": 100, "environmental_pressure": 20, "mutation_scars": 2}
    snapshot = exporter.export_echo("player_alpha", dummy_dash)
    exporter.save_echo(snapshot, "outputs/domain_echoes/")
