import unittest
import os
import json
from engine.room_graph.runtime import room_graph_builder

class TestRoomGraphBuilder(unittest.TestCase):
    def setUp(self):
        self.floor_record = {"floor_id": 1, "status": "active"}
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))

    def test_make_room_node(self):
        node = room_graph_builder.make_room_node("test_node", "combat_room", difficulty_rating=0.5)
        self.assertEqual(node["node_id"], "test_node")
        self.assertEqual(node["node_type"], "combat_room")
        self.assertEqual(node["difficulty_rating"], 0.5)
        self.assertIsInstance(node["connections"], list)

    def test_build_room_graph_success(self):
        result = room_graph_builder.build_room_graph(self.floor_record)
        self.assertTrue(result["ok"])
        graph = result["payload"]
        self.assertEqual(graph["floor_id"], 1)
        self.assertEqual(graph["domain_archetype"], "tower_domain")
        self.assertEqual(graph["entry_node_id"], "entry_a")
        self.assertEqual(graph["exit_node_id"], "exit_a")
        
        # Check for required nodes
        node_types = [node["node_type"] for node in graph["nodes"]]
        self.assertIn("entry_room", node_types)
        self.assertIn("combat_room", node_types)
        self.assertIn("pressure_room", node_types)
        self.assertIn("recovery_room", node_types)
        self.assertIn("exit_room", node_types)

    def test_build_room_graph_determinism(self):
        result1 = room_graph_builder.build_room_graph(self.floor_record)
        result2 = room_graph_builder.build_room_graph(self.floor_record)
        self.assertEqual(result1["payload"], result2["payload"])

    def test_build_room_graph_with_survivor_mark(self):
        result = room_graph_builder.build_room_graph(self.floor_record, include_survivor_mark_room=True)
        self.assertTrue(result["ok"])
        graph = result["payload"]
        self.assertTrue(any(node["node_type"] == "survivor_mark_room" for node in graph["nodes"]))
        self.assertIn("survivor_mark_a", graph["survivor_mark_nodes"])
        
        # Check if at least one node supports survivor mark
        self.assertTrue(any(node["supports_survivor_mark"] is True for node in graph["nodes"]))

    def test_validate_room_graph(self):
        result = room_graph_builder.build_room_graph(self.floor_record)
        graph = result["payload"]
        validation = room_graph_builder.validate_room_graph(graph)
        self.assertTrue(validation["ok"], f"Validation failed: {validation.get('message')}")

    def test_failure_missing_floor_record(self):
        result = room_graph_builder.build_room_graph(None)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "MissingFloorRecord")

    def test_failure_invalid_floor_id(self):
        result = room_graph_builder.build_room_graph({"no_id": True})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "InvalidFloorId")

    def test_failure_unsupported_archetype(self):
        result = room_graph_builder.build_room_graph(self.floor_record, domain_archetype="swamp_domain")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_type"], "UnsupportedDomainArchetype")

    def test_summarize_room_graph(self):
        result = room_graph_builder.build_room_graph(self.floor_record)
        summary = room_graph_builder.summarize_room_graph(result["payload"])
        self.assertIn("Room Graph", summary)
        self.assertIn("nodes", summary)

    def test_debug_enabled(self):
        # Should not crash with debug=True even if logger is missing
        result = room_graph_builder.build_room_graph(self.floor_record, debug=True)
        self.assertTrue(result["ok"])

if __name__ == '__main__':
    unittest.main()
