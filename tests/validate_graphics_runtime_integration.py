import unittest
from engine.runtime.playable_slice_manager import PlayableSliceManager
import json
import os

class TestGraphicsRuntimeIntegration(unittest.TestCase):
    def setUp(self):
        # Ensure contract exists for testing
        os.makedirs("engine/runtime/contracts", exist_ok=True)
        contract_path = "engine/runtime/contracts/vertical_slice_contract.json"
        if not os.path.exists(contract_path):
            with open(contract_path, "w") as f:
                json.dump({"test": "data"}, f)
                
    def test_integration_auditor(self):
        psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
        psm.run_playable_loop()
        
        # Test audit
        mismatches = psm.auditor.audit()
        # Mismatches list should exist
        self.assertIsInstance(mismatches, list)
        print("Integration Mismatches:", mismatches)

if __name__ == "__main__":
    unittest.main()
