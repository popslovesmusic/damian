import unittest
import json
import os
from engine.presentation.visual_asset_selection_manager import VisualAssetSelectionManager

class TestVisualAssetSelectionLock(unittest.TestCase):
    def setUp(self):
        # Paths for test files (relative to root)
        self.contract_path = "engine/presentation/visual_asset_selection_contract.json"
        self.approved_set_path = "engine/presentation/approved_runtime_visual_set.json"
        self.log_path = "engine/presentation/rejected_visual_asset_log.json"
        self.rules_path = "engine/presentation/visual_consistency_rules.json"

    def test_asset_selection_lock(self):
        manager = VisualAssetSelectionManager(
            self.contract_path, 
            self.approved_set_path, 
            self.log_path, 
            self.rules_path
        )
        
        # Test approved
        self.assertTrue(manager.is_asset_approved("enemies", "spider_large"))
        
        # Test unapproved
        self.assertFalse(manager.is_asset_approved("enemies", "unknown_monster"))
        
        # Test logging
        manager.log_rejection("enemies", "unknown_monster", "not in approved list")
        
        with open(self.log_path, 'r') as f:
            log = json.load(f)
            self.assertTrue(any(item["asset_id"] == "unknown_monster" for item in log))

if __name__ == "__main__":
    unittest.main()
