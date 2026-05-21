import unittest
from engine.runtime.inventory_manager import InventoryManager

class TestInventoryEquipment(unittest.TestCase):
    def setUp(self):
        self.inv = InventoryManager(
            "engine/runtime/inventory_contract.json",
            "engine/runtime/equipment_profile.json",
            "engine/runtime/consumable_rules.json",
            "engine/runtime/burden_capacity_rules.json"
        )

    def test_inventory_flow(self):
        # Test pickup
        self.assertTrue(self.inv.add_item("FOOD", 10))
        self.assertEqual(self.inv.items["FOOD"], 10)
        
        # Test usage
        effect = self.inv.use_item("FOOD")
        self.assertEqual(effect["effect"], "heal")
        self.assertEqual(self.inv.items["FOOD"], 9)
        
        # Test burden limit
        self.assertTrue(self.inv.add_item("SCRAP", 40))
        self.assertFalse(self.inv.add_item("SCRAP", 2)) # Exceeds 50 total (40+9 = 49 + 2 = 51)

if __name__ == "__main__":
    unittest.main()
