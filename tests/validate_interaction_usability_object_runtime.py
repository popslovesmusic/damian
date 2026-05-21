import unittest
import json
from engine.runtime.interaction_object_manager import InteractionObjectManager
from engine.runtime.contact_boundary_manager import ContactBoundaryManager

class TestInteractionUsability(unittest.TestCase):
    def setUp(self):
        self.cbm = ContactBoundaryManager(
            "engine/runtime/contact_boundary_contract.json",
            "engine/runtime/boundary_priority_rules.json",
            "engine/runtime/interaction_volume_profile.json",
            "engine/runtime/hazard_contact_profile.json"
        )
        self.iom = InteractionObjectManager(
            "engine/runtime/interaction_object_contract.json",
            "engine/runtime/object_interaction_rules.json",
            "engine/runtime/usable_object_profile.json",
            "engine/runtime/interaction_prompt_rules.json",
            self.cbm
        )

    def test_interaction_usability(self):
        # Add interactable object boundary
        self.cbm.add_boundary("R001", "interaction", {"object_id": "door_small_01"})
        
        # Test interactable
        res = self.iom.can_interact("R001", {"x": 1, "y": 1})
        self.assertTrue(res["can_interact"])
        self.assertEqual(res["object_type"], "door")
        
        # Test non-interactable
        res = self.iom.can_interact("R002", {"x": 0, "y": 0})
        self.assertFalse(res["can_interact"])

if __name__ == "__main__":
    unittest.main()
