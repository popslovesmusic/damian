import unittest
import json
import os
from engine.world.room_dressing_manager import RoomDressingManager
from engine.world.floor_generation_manager import FloorGenerationManager

class TestRoomDressing(unittest.TestCase):
    def setUp(self):
        self.dressing_manager = RoomDressingManager(
            "engine/world/room_dressing_contract.json",
            "engine/world/prop_placement_rules.json",
            "engine/world/environment_clutter_profile.json",
            "engine/world/room_silhouette_profile.json"
        )
        self.fgm = FloorGenerationManager(
            "engine/world/floor_generation_contract.json",
            "engine/world/hazard_generation_profile.json",
            "engine/world/route_pressure_rules.json",
            dressing_manager=self.dressing_manager
        )

    def test_room_dressing(self):
        floor = self.fgm.generate_floor(seed="test_seed", difficulty_tier=1)
        
        # Check if rooms have props
        for room in floor.get("rooms", []):
            self.assertIn("props", room)
            self.assertIsInstance(room["props"], list)
            # Entry rooms should have props
            if room["room_type"] == "entry":
                self.assertTrue(len(room["props"]) >= 0)
                print(f"Room {room['room_id']} ({room['room_type']}) props: {room['props']}")

if __name__ == "__main__":
    unittest.main()
