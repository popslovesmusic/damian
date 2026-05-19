import unittest
from engine.room_graph.runtime import room_graph_mutation_evidence

class TestRoomGraphMutationEvidence(unittest.TestCase):
    def setUp(self):
        self.floor_record = {
            "floor_id": 1,
            "content_pack_id": "damian",
            "domain_archetype": "tower_domain",
            "layout_seed": "seed_1"
        }
        self.floor_memory_before = {
            "floor_id": 1,
            "mutation_level": 0,
            "unclaimed_easter_eggs": [],
            "active_mutations": []
        }
        self.floor_memory_after = {
            "floor_id": 1,
            "mutation_level": 1,
            "unclaimed_easter_eggs": ["mark_1"],
            "active_mutations": ["minor_corridor_shift_stub"]
        }

    def test_make_before_after_room_graphs(self):
        result = room_graph_mutation_evidence.make_before_after_room_graphs(
            self.floor_record, self.floor_memory_before, self.floor_memory_after
        )
        self.assertTrue(result["ok"])
        before_graph = result["before_graph"]
        after_graph = result["after_graph"]
        
        self.assertEqual(before_graph["mutation_level"], 0)
        self.assertEqual(after_graph["mutation_level"], 1)
        
        # Before should not have survivor mark room (no unclaimed)
        self.assertFalse(any(n["node_type"] == "survivor_mark_room" for n in before_graph["nodes"]))
        # After should have survivor mark room (has unclaimed)
        self.assertTrue(any(n["node_type"] == "survivor_mark_room" for n in after_graph["nodes"]))

    def test_diff_room_graphs_detection(self):
        graphs = room_graph_mutation_evidence.make_before_after_room_graphs(
            self.floor_record, self.floor_memory_before, self.floor_memory_after
        )
        diff = room_graph_mutation_evidence.diff_room_graphs(graphs["before_graph"], graphs["after_graph"])
        
        self.assertTrue(diff["graph_changed"])
        self.assertTrue(diff["survivor_mark_room_added"])
        self.assertEqual(diff["mutation_level_delta"], 1)
        self.assertIn("survivor_mark_room", diff["new_room_types"])

    def test_make_room_graph_mutation_evidence_success(self):
        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(
            self.floor_record, self.floor_memory_before, self.floor_memory_after
        )
        self.assertTrue(evidence["ok"])
        self.assertEqual(evidence["floor_id"], 1)
        self.assertTrue(evidence["graph_changed"])
        self.assertTrue(evidence["survivor_mark_room_added"])
        self.assertEqual(evidence["mutation_level_delta"], 1)
        self.assertTrue(len(evidence["readable_summary"]) > 0)

    def test_make_room_graph_mutation_evidence_no_change(self):
        # Same memory before and after
        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(
            self.floor_record, self.floor_memory_before, self.floor_memory_before
        )
        self.assertTrue(evidence["ok"])
        self.assertFalse(evidence["graph_changed"])
        self.assertEqual(evidence["mutation_level_delta"], 0)

    def test_failure_invalid_input(self):
        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(None, None, None)
        self.assertFalse(evidence["ok"])
        self.assertEqual(evidence["error"]["type"], "InvalidInput")

    def test_debug_hooks(self):
        # Should not crash with debug=True
        evidence = room_graph_mutation_evidence.make_room_graph_mutation_evidence(
            self.floor_record, self.floor_memory_before, self.floor_memory_after, debug=True
        )
        self.assertTrue(evidence["ok"])

if __name__ == '__main__':
    unittest.main()
