import unittest
import json
import os
from engine.runtime.playable_slice_manager import PlayableSliceManager

class TestAnimationScaffold(unittest.TestCase):
    def setUp(self):
        # Ensure contract exists for testing
        os.makedirs("engine/runtime/contracts", exist_ok=True)
        contract_path = "engine/runtime/contracts/vertical_slice_contract.json"
        if not os.path.exists(contract_path):
            with open(contract_path, "w") as f:
                json.dump({"test": "data"}, f)
                
    def test_animation_scaffold(self):
        psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
        report = psm.run_playable_loop()
        
        self.assertTrue(len(report["visual_log"]) > 0)
        # Check if first log entry has animation state
        first_entry = report["visual_log"][0]
        self.assertIn("isometric", first_entry)
        
        # Check if animations are being rendered
        self.assertIn("Animations", first_entry["isometric"])
        
        print("Isometric View with Animations:\n", first_entry["isometric"])

if __name__ == "__main__":
    unittest.main()
