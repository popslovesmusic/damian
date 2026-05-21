import unittest
import os
import json

class TestFirstPlayablePackaging(unittest.TestCase):
    def test_package_creation(self):
        # Check dist directory existence
        self.assertTrue(os.path.exists("dist/Damian_Tower_Walkable_Prototype/"))
        # Check scripts existence
        self.assertTrue(os.path.exists("dist/Damian_Tower_Walkable_Prototype/run_tower.bat"))
        # Check engine directory copied
        self.assertTrue(os.path.exists("dist/Damian_Tower_Walkable_Prototype/engine/"))

if __name__ == "__main__":
    unittest.main()
