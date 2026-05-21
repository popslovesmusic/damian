import unittest
import json
import os
from engine.presentation.room_identity_auditor import RoomIdentityAuditor

class TestRoomIdentity(unittest.TestCase):
    def setUp(self):
        self.auditor = RoomIdentityAuditor(
            "engine/presentation/room_identity_contract.json",
            "engine/presentation/room_readability_rules.json",
            "engine/presentation/room_identity_score_profile.json"
        )

    def test_room_identity(self):
        # Combat room with props should pass
        room = {
            "room_type": "combat",
            "props": ["cover_debris", "weapon_broken", "blood_mark"]
        }
        result = self.auditor.audit_room(room)
        self.assertEqual(result["status"], "PASS")
        
        # Hazard room with props should pass
        room = {
            "room_type": "hazard",
            "props": ["steam_pipe", "collapse_debris"]
        }
        result = self.auditor.audit_room(room)
        self.assertEqual(result["status"], "PASS")
        
        # Room with missing required props should fail
        room = {
            "room_type": "combat",
            "props": ["weapon_broken"]
        }
        result = self.auditor.audit_room(room)
        self.assertEqual(result["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
