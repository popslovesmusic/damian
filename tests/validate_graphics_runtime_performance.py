import unittest
import json
import os
from engine.presentation.graphics_performance_manager import GraphicsPerformanceManager

class TestGraphicsRuntimePerformance(unittest.TestCase):
    def setUp(self):
        # Paths for test files (relative to root)
        self.contract_path = "engine/presentation/graphics_performance_contract.json"
        self.budget_path = "engine/presentation/render_budget_profile.json"
        self.metrics_path = "engine/presentation/visual_readability_metrics.json"

    def test_performance_budget(self):
        manager = GraphicsPerformanceManager(
            self.contract_path,
            self.budget_path,
            self.metrics_path
        )
        
        # Test budget check (initially within budget)
        self.assertTrue(manager.check_budget())
        
        # Test exceeding budget
        manager.report_usage("effects", 50) # Max 32
        self.assertFalse(manager.check_budget())
        
        # Test reset
        manager.reset_frame_usage()
        self.assertTrue(manager.check_budget())

if __name__ == "__main__":
    unittest.main()
