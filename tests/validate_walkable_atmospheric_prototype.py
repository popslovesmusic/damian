import unittest
from engine.runtime.playable_slice_manager import PlayableSliceManager
from engine.runtime.walkable_prototype_manager import WalkablePrototypeManager
import os

class TestWalkablePrototype(unittest.TestCase):
    def setUp(self):
        self.psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
        self.wpm = WalkablePrototypeManager(
            "engine/runtime/walkable_prototype_contract.json",
            "engine/runtime/player_controller_profile.json",
            "engine/runtime/prototype_launch_config.json",
            self.psm
        )

    def test_prototype_setup(self):
        # Verify components loaded
        self.assertIsNotNone(self.wpm.contract)
        self.assertIsNotNone(self.wpm.psm)
        
    def test_basic_interaction(self):
        # Verify interaction works via PSM
        result = self.wpm.psm.simulate_player_input("MOVE", "NORTH")
        self.assertEqual(result["status"], "MOVED")

if __name__ == "__main__":
    unittest.main()
