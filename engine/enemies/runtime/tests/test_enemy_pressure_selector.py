import unittest
import json
from engine.enemies.runtime import enemy_pressure_selector

class TestEnemyPressureSelector(unittest.TestCase):
    def setUp(self):
        self.base_floor_memory = {
            "floor_id": 1,
            "visit_count": 1,
            "death_count": 0,
            "victory_count": 0,
            "stability": 1.0,
            "deviation": 0.0,
            "mutation_level": 0,
            "known_layout_seed": "seed_1",
            "active_mutations": [],
            "discovered_easter_eggs": [],
            "unclaimed_easter_eggs": [],
            "residue_history": []
        }

    def test_calculate_pressure_bias_low(self):
        biases = enemy_pressure_selector.calculate_pressure_bias(self.base_floor_memory)
        self.assertGreater(biases["pressure_unit"], biases["ambush_unit"])
        self.assertEqual(biases["attrition_unit"], 0.2)

    def test_calculate_pressure_bias_potion(self):
        fm = self.base_floor_memory.copy()
        fm["residue_history"] = [
            {"residue_id": "r1", "tags": ["high_potion_usage"]},
            {"residue_id": "r2", "tags": ["potion_dependency"]},
            {"residue_id": "r3", "tags": ["potion_overuse"]}
        ]
        biases = enemy_pressure_selector.calculate_pressure_bias(fm)
        self.assertGreater(biases["attrition_unit"], 0.6)

    def test_calculate_pressure_bias_strategy(self):
        fm = self.base_floor_memory.copy()
        fm["residue_history"] = [
            {"residue_id": "r1", "tags": ["repeated_strategy"]},
            {"residue_id": "r2", "tags": ["repeated_strategy"]}
        ]
        biases = enemy_pressure_selector.calculate_pressure_bias(fm)
        self.assertGreater(biases["counter_unit"], 0.6)

    def test_calculate_pressure_bias_instability(self):
        fm = self.base_floor_memory.copy()
        fm["stability"] = 0.5
        biases = enemy_pressure_selector.calculate_pressure_bias(fm)
        self.assertGreater(biases["ambush_unit"], 0.5)

    def test_select_enemy_archetype_determinism(self):
        res1 = enemy_pressure_selector.select_enemy_archetype(self.base_floor_memory)
        res2 = enemy_pressure_selector.select_enemy_archetype(self.base_floor_memory)
        self.assertEqual(res1, res2)

    def test_build_enemy_pressure_profile(self):
        profile = enemy_pressure_selector.build_enemy_pressure_profile("attrition_unit", self.base_floor_memory)
        self.assertEqual(profile["enemy_archetype_id"], "attrition_unit")
        self.assertGreaterEqual(profile["base_pressure_rating"], 0.0)
        self.assertLessEqual(profile["base_pressure_rating"], 1.0)
        self.assertFalse(profile["bounded_rules"]["unavoidable_defeat"])
        self.assertIsInstance(profile["adaptation_reasoning"], list)

    def test_summarize_enemy_pressure_profile(self):
        profile = enemy_pressure_selector.build_enemy_pressure_profile("pressure_unit", self.base_floor_memory)
        summary = enemy_pressure_selector.summarize_enemy_pressure_profile(profile)
        self.assertIn("pressure_unit", summary)
        self.assertIn("Reasoning", summary)

    def test_invalid_floor_memory_fails_safely(self):
        res = enemy_pressure_selector.select_enemy_archetype(None)
        self.assertIsNone(res)
        
        biases = enemy_pressure_selector.calculate_pressure_bias(None)
        self.assertEqual(biases, {})

    def test_debug_hooks(self):
        # Should not crash
        enemy_pressure_selector.select_enemy_archetype(self.base_floor_memory, debug=True)

if __name__ == '__main__':
    unittest.main()
