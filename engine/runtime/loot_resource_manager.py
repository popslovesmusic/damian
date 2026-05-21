import json
import random

class LootResourceManager:
    def __init__(self, contract_path, spawn_path, decay_path, profile_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        with open(spawn_path, 'r') as f:
            self.spawn_rules = json.load(f)
        with open(decay_path, 'r') as f:
            self.decay_rules = json.load(f)
        with open(profile_path, 'r') as f:
            self.loot_profile = json.load(f)

    def get_container_loot(self, container_type):
        """Returns loot for a container type."""
        loot = self.loot_profile.get(container_type, {}).copy()
        
        # Apply faction tax (mock)
        for res in loot:
            loot[res] = max(1, int(loot[res] * 0.8))
        return loot
