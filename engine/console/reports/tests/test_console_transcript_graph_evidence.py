import unittest
import os
import json
import shutil
from engine.console.reports import console_transcript_reporter

class TestConsoleTranscriptGraphEvidence(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_transcript_graph_evidence"
        self.output_dir = os.path.join(self.test_dir, "transcripts")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Paths for startup
        self.paths = {
            "tower_state": os.path.join(self.test_dir, "tower_state.json"),
            "player_progression": os.path.join(self.test_dir, "player_progression.json"),
            "system_registry": os.path.join(self.test_dir, "system_registry.json"),
            "state_machine_states": "engine/core/state_machine/game_loop_states.json",
            "state_machine_transitions": "engine/core/state_machine/game_loop_transitions.json",
            "tower_state_schema": "engine/save/schemas/tower_state.schema.json",
            "player_progression_schema": "engine/player/contracts/player_progression_state.schema.json",
            "domain_state": os.path.join(self.test_dir, "domain_state.json"),
            "domain_state_schema": "engine/domain/contracts/domain_state.schema.json"
        }
        
        # Valid tower state
        with open(self.paths["tower_state"], 'w') as f:
            json.dump({
                "tower_state_id": "test_tower",
                "engine_version": "0.0.1",
                "content_pack_id": "damian",
                "current_floor": 1,
                "highest_floor_reached": 1,
                "total_runs": 1,
                "total_deaths": 0,
                "floor_memory": [],
                "global_residue": {},
                "last_outcome": "NONE",
                "updated_at": "2026-05-19T00:00:00Z"
            }, f)
            
        # Valid player progression
        with open(self.paths["player_progression"], 'w') as f:
            json.dump({
                "player_id": "test_player",
                "profile_id": "profile_123",
                "content_pack_id": "damian",
                "level": 1,
                "highest_floor_reached": 1,
                "active_orientation": "default",
                "stats": {
                    "health": 100.0, "damage": 10.0, "defense": 10.0, "speed": 1.0, "recovery": 1.0
                },
                "unlocked_skills": [],
                "equipped_items": [],
                "residue_pressure": {
                    "dominant_build_visibility": 0.0, "power_use_strain": 0.0, "overoptimization_pressure": 0.0
                },
                "forbidden_flags": {
                    "permanent_invulnerability": False, "infinite_damage_scaling": False, 
                    "residue_immunity": False, "death_consequence_immunity": False
                }
            }, f)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_transcript_captures_graph_evidence_after_combat_defeat(self):
        commands = [
            "status",
            "combat dangerous", # Should result in defeat and mutation
            "diff",             # Should report graph evidence
            "quit"
        ]
        
        transcript = console_transcript_reporter.run_console_transcript(
            commands, paths=self.paths, output_dir=self.output_dir, transcript_id="test_graph_evidence"
        )
        
        self.assertTrue(transcript["ok"])
        self.assertEqual(transcript["combat_sessions_observed"], 1)
        self.assertEqual(len(transcript["combat_outcomes_observed"]), 1)
        self.assertEqual(transcript["combat_outcomes_observed"][0], "DEFEAT_DROP")
        
        # Verify graph evidence capture
        self.assertTrue(transcript["room_graph_evidence_observed"])
        self.assertGreaterEqual(transcript["room_graph_changes_observed"], 1)
        self.assertGreaterEqual(transcript["survivor_mark_rooms_observed"], 1)
        self.assertTrue(len(transcript["graph_diff_summaries"]) > 0)
        
        # Verify existing observations are still present
        self.assertTrue(transcript["mutation_after_combat_observed"])
        self.assertTrue(transcript["survivor_mark_after_combat_observed"])

if __name__ == '__main__':
    unittest.main()
