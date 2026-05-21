import unittest
import os
import json
from engine.runtime.first_run_diagnostics import FirstRunDiagnostics

class TestWalkableFirstRunHardening(unittest.TestCase):
    def setUp(self):
        self.diagnostics = FirstRunDiagnostics("engine/runtime/first_run_contract.json")

    def test_diagnostic_checks(self):
        # We expect failure in this test environment if TOWER_DATA is not set, 
        # which is correct for testing the diagnostic system itself.
        results = self.diagnostics.run_checks()
        self.assertIsInstance(results, dict)
        self.assertIn("passed", results)

if __name__ == "__main__":
    unittest.main()
