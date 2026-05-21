import unittest
from engine.runtime.hazard_contact_manager import HazardContactManager
from engine.runtime.contact_boundary_manager import ContactBoundaryManager

class TestHazardContactDamage(unittest.TestCase):
    def setUp(self):
        self.cbm = ContactBoundaryManager(
            "engine/runtime/contact_boundary_contract.json",
            "engine/runtime/boundary_priority_rules.json",
            "engine/runtime/interaction_volume_profile.json",
            "engine/runtime/hazard_contact_profile.json"
        )
        self.hcm = HazardContactManager(
            "engine/runtime/hazard_contact_contract.json",
            "engine/runtime/hazard_damage_rules.json",
            "engine/runtime/environmental_damage_profile.json",
            "engine/runtime/hazard_warning_profile.json",
            self.cbm
        )

    def test_hazard_contact(self):
        # Test hazard contact
        self.cbm.add_boundary("R001", "hazard", {"type": "steam"})
        
        effect = self.hcm.resolve_hazard("R001", {"x": 0, "y": 0})
        self.assertIsNotNone(effect)
        self.assertEqual(effect["damage"], 5)
        self.assertEqual(effect["pressure"], 10)

        # Test no contact (different room/position)
        effect = self.hcm.resolve_hazard("R002", {"x": 0, "y": 0})
        self.assertIsNone(effect)

if __name__ == "__main__":
    unittest.main()
