import unittest
import json
import os
from engine.world.landmark_storytelling_manager import LandmarkStorytellingManager

class TestEnvironmentalStorytelling(unittest.TestCase):
    def setUp(self):
        # Paths for test files (relative to root)
        self.contract_path = "engine/world/landmark_storytelling_contract.json"
        self.generation_path = "engine/world/landmark_generation_rules.json"
        self.story_path = "engine/world/environmental_story_profile.json"
        self.faction_path = "engine/world/faction_ruin_profile.json"
        self.ritual_path = "engine/world/ritual_space_profile.json"

    def test_landmark_generation(self):
        manager = LandmarkStorytellingManager(
            self.contract_path,
            self.generation_path,
            self.story_path,
            self.faction_path,
            self.ritual_path
        )
        
        room_data = {"room_id": "R001"}
        world_memory = {}
        
        # Test generation (may return None, but shouldn't crash)
        landmark = manager.generate_landmark_for_room(room_data, world_memory)
        
        if landmark:
            self.assertIn("landmark_id", landmark)
            self.assertIn("type", landmark)
            self.assertIn("components", landmark)
            print("Generated Landmark:", landmark)
        else:
            print("No landmark generated this time.")

if __name__ == "__main__":
    unittest.main()
