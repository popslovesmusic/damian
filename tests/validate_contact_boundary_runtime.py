import unittest
import json
import os
from engine.runtime.contact_boundary_manager import ContactBoundaryManager

class TestContactBoundary(unittest.TestCase):
    def setUp(self):
        self.boundary_manager = ContactBoundaryManager(
            "engine/runtime/contact_boundary_contract.json",
            "engine/runtime/boundary_priority_rules.json",
            "engine/runtime/interaction_volume_profile.json",
            "engine/runtime/hazard_contact_profile.json"
        )

    def test_contact_boundary(self):
        # Test adding and checking contact
        self.boundary_manager.add_boundary("R001", "collision", {"solid": True})
        
        contact = self.boundary_manager.check_contact("R001", {"x": 1, "y": 1})
        self.assertIsNotNone(contact)
        self.assertEqual(contact["type"], "collision")
        self.assertTrue(contact["data"]["solid"])

if __name__ == "__main__":
    unittest.main()
