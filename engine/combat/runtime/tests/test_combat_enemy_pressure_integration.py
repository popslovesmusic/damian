import unittest
import os
import json
import uuid
from engine.combat.runtime import mvp_combat_resolution_stub

class TestCombatEnemyPressureIntegration(unittest.TestCase):
    def setUp(self):
        self.player_state = {"player_id": "test_player", "health": 100.0}
        self.base_profile = {
            "enemy_archetype_id": "pressure_unit",
            "base_pressure_rating": 0.3,
            "mutation_level": 0,
            "residue_pressure_bias": 0.0,
            "resource_pressure_bias": 0.0,
            "adaptation_reasoning": ["Standard threat"],
            "bounded_rules": {"unavoidable_defeat": False, "requires_god_mode": False, "bypasses_pipeline": False}
        }

    def test_make_combat_session_with_profile(self):
        session = mvp_combat_resolution_stub.make_combat_session(
            floor_id=1, player_state=self.player_state, enemy_pressure_profile=self.base_profile
        )
        self.assertEqual(session["enemy_archetype_id"], "pressure_unit")
        self.assertEqual(session["enemy_pressure_rating"], 0.3)
        self.assertIn("Standard threat", session["enemy_adaptation_reasoning"])

    def test_attrition_unit_increases_resource_pressure(self):
        profile = self.base_profile.copy()
        profile["enemy_archetype_id"] = "attrition_unit"
        
        session = mvp_combat_resolution_stub.make_combat_session(1, self.player_state, enemy_pressure_profile=profile)
        result = mvp_combat_resolution_stub.resolve_combat_session(session)
        
        self.assertTrue(result["resource_pressure_observed"])
        self.assertEqual(result["enemy_archetype_id"], "attrition_unit")

    def test_counter_unit_increases_residue_pressure(self):
        profile = self.base_profile.copy()
        profile["enemy_archetype_id"] = "counter_unit"
        
        session = mvp_combat_resolution_stub.make_combat_session(1, self.player_state, enemy_pressure_profile=profile)
        result = mvp_combat_resolution_stub.resolve_combat_session(session)
        
        self.assertTrue(result["residue_pressure_observed"])
        self.assertEqual(result["enemy_archetype_id"], "counter_unit")

    def test_ambush_unit_high_risk_at_low_health(self):
        profile = self.base_profile.copy()
        profile["enemy_archetype_id"] = "ambush_unit"
        profile["base_pressure_rating"] = 0.75 # Effective will be 0.95 (> 0.90)
        
        # Low health + ambush should trigger DEFEAT_DROP
        low_health_player = {"player_id": "p1", "health": 20.0}
        session = mvp_combat_resolution_stub.make_combat_session(1, low_health_player, enemy_pressure_profile=profile)
        result = mvp_combat_resolution_stub.resolve_combat_session(session)
        
        self.assertEqual(result["resolved_outcome"], "DEFEAT_DROP")

    def test_pressure_unit_remains_baseline(self):
        session = mvp_combat_resolution_stub.make_combat_session(1, self.player_state, enemy_pressure_profile=self.base_profile)
        result = mvp_combat_resolution_stub.resolve_combat_session(session)
        
        self.assertEqual(result["resolved_outcome"], "VICTORY_ASCEND")
        self.assertFalse(result["resource_pressure_observed"])

    def test_resolve_combat_into_pipeline_integration(self):
        # We need a tower_state for this
        tower_state = {
            "tower_state_id": "t1", "engine_version": "0.0.1", "content_pack_id": "damian",
            "current_floor": 1, "highest_floor_reached": 1, "total_runs": 1, "total_deaths": 0,
            "floor_memory": [], "global_residue": {}, "last_outcome": "NONE", "updated_at": "2026-05-19T00:00:00Z"
        }
        
        profile = self.base_profile.copy()
        profile["enemy_archetype_id"] = "ambush_unit"
        profile["base_pressure_rating"] = 0.95
        
        session = mvp_combat_resolution_stub.make_combat_session(1, {"health": 10.0}, enemy_pressure_profile=profile)
        result = mvp_combat_resolution_stub.resolve_combat_into_pipeline(tower_state, session)
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["resolved_outcome"], "DEFEAT_DROP")
        # Pipeline should have incremented death count or applied mutation
        pipeline_res = result["pipeline_result"]
        self.assertTrue(pipeline_res["ok"])
        self.assertEqual(pipeline_res["tower_state"]["total_deaths"], 1)

    def test_debug_hooks(self):
        session = mvp_combat_resolution_stub.make_combat_session(1, self.player_state, debug=True)
        mvp_combat_resolution_stub.resolve_combat_session(session, debug=True)

if __name__ == '__main__':
    unittest.main()
