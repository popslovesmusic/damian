import unittest
from engine.runtime.loot_resource_manager import LootResourceManager
import json

class TestLootResourceEconomy(unittest.TestCase):
    def setUp(self):
        self.lrm = LootResourceManager(
            "engine/runtime/loot_resource_contract.json",
            "engine/runtime/resource_spawn_rules.json",
            "engine/runtime/resource_decay_rules.json",
            "engine/runtime/container_loot_profile.json"
        )

    def test_loot_resource(self):
        # Test loot retrieval
        loot = self.lrm.get_container_loot("crate")
        self.assertIn("FOOD", loot)
        # Verify faction tax (5 * 0.8 = 4)
        self.assertEqual(loot["FOOD"], 4)

if __name__ == "__main__":
    unittest.main()
