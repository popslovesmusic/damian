import unittest
import json
import os
from engine.runtime.traversal_contact_manager import TraversalContactManager
from engine.runtime.contact_boundary_manager import ContactBoundaryManager

class TestTraversalContactMovement(unittest.TestCase):
    def setUp(self):
        self.cbm = ContactBoundaryManager(
            "engine/runtime/contact_boundary_contract.json",
            "engine/runtime/boundary_priority_rules.json",
            "engine/runtime/interaction_volume_profile.json",
            "engine/runtime/hazard_contact_profile.json"
        )
        self.tcm = TraversalContactManager(
            "engine/runtime/traversal_contact_contract.json",
            "engine/runtime/movement_resolution_rules.json",
            "engine/runtime/stamina_movement_profile.json",
            "engine/runtime/route_contact_profile.json",
            self.cbm
        )

    def test_movement_resolution(self):
        # Test free movement
        res = self.tcm.resolve_movement("R001", {"x": 0, "y": 0}, "walk")
        self.assertEqual(res["status"], "MOVED")
        
        # Test collision blocking
        self.cbm.add_boundary("R001", "collision", {"solid": True})
        res = self.tcm.resolve_movement("R001", {"x": 1, "y": 1}, "walk")
        self.assertEqual(res["status"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
