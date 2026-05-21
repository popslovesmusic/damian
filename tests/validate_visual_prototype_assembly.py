import unittest
import json
import os
from engine.runtime.playable_slice_manager import PlayableSliceManager

class TestVisualPrototypeAssembly(unittest.TestCase):
    def setUp(self):
        # Ensure contract exists for testing
        os.makedirs("engine/runtime/contracts", exist_ok=True)
        contract_path = "engine/runtime/contracts/vertical_slice_contract.json"
        if not os.path.exists(contract_path):
            with open(contract_path, "w") as f:
                json.dump({"test": "data"}, f)
                
    def test_visual_assembly(self):
        psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
        report = psm.run_playable_loop()
        
        self.assertTrue(len(report["visual_log"]) > 0)
        # Check if first log entry has both types
        first_entry = report["visual_log"][0]
        self.assertIn("scaffold", first_entry)
        self.assertIn("isometric", first_entry)
        
        print("Isometric View:\n", first_entry["isometric"])

if __name__ == "__main__":
    unittest.main()
