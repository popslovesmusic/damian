import unittest
import json
import os
from engine.runtime.combat_contact_manager import CombatContactManager
from engine.runtime.contact_boundary_manager import ContactBoundaryManager

class TestCombatContactDamage(unittest.TestCase):
    def setUp(self):
        self.cbm = ContactBoundaryManager(
            "engine/runtime/contact_boundary_contract.json",
            "engine/runtime/boundary_priority_rules.json",
            "engine/runtime/interaction_volume_profile.json",
            "engine/runtime/hazard_contact_profile.json"
        )
        self.ccm = CombatContactManager(
            "engine/runtime/combat_contact_contract.json",
            "engine/runtime/damage_resolution_rules.json",
            "engine/runtime/weapon_contact_profile.json",
            "engine/runtime/hurt_volume_profile.json",
            self.cbm
        )

    def test_combat_resolution(self):
        # Mock a hit
        self.cbm.add_boundary("R001", "hurt_volume", {"solid": True})
        
        # Test hit resolution
        damage = self.ccm.resolve_attack("player", "enemy_0", "R001", "sword")
        self.assertIsNotNone(damage)
        self.assertEqual(damage, 10) # Base damage

        # Test missed attack (no boundary)
        self.cbm.boundaries["R001"] = [] # Clear boundaries
        damage = self.ccm.resolve_attack("player", "enemy_0", "R001", "sword")
        self.assertIsNone(damage)

if __name__ == "__main__":
    unittest.main()
