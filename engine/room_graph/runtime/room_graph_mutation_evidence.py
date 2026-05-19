import uuid
import os

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

from engine.room_graph.runtime import room_graph_builder

PATCH_ID = "TOWER-ENGINE-043"
SYSTEM_NAME = "room_graph_mutation_evidence"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass
    elif not _debug_logger_available and debug_enabled:
        print(f"DEBUG [{SYSTEM_NAME}]: {message}")

def make_before_after_room_graphs(floor_record, floor_memory_before, floor_memory_after, debug=False):
    """
    Builds before and after room graphs based on mutation state.
    """
    _log_debug_event("INFO", "MakeBeforeAfterGraphs", f"Building graphs for floor {floor_record.get('floor_id')}", debug_enabled=debug)

    # Before graph
    has_unclaimed_before = bool(floor_memory_before.get("unclaimed_easter_eggs", []))
    # Requirement: before graph is built without survivor_mark_room when floor has no unclaimed survivor marks
    before_result = room_graph_builder.build_room_graph(
        floor_record, 
        include_survivor_mark_room=has_unclaimed_before, 
        debug=debug
    )
    if not before_result["ok"]:
        return before_result
    
    before_graph = before_result["payload"]
    # Adjust before graph mutation level to match floor_memory_before
    before_graph["mutation_level"] = floor_memory_before.get("mutation_level", 0)

    # After graph
    has_unclaimed_after = bool(floor_memory_after.get("unclaimed_easter_eggs", []))
    # Requirement: after graph includes survivor_mark_room when floor has unclaimed survivor marks
    after_result = room_graph_builder.build_room_graph(
        floor_record, 
        include_survivor_mark_room=has_unclaimed_after, 
        debug=debug
    )
    if not after_result["ok"]:
        return after_result
    
    after_graph = after_result["payload"]
    # Adjust after graph mutation level to match floor_memory_after
    after_graph["mutation_level"] = floor_memory_after.get("mutation_level", 0)

    return {"ok": True, "before_graph": before_graph, "after_graph": after_graph}

def diff_room_graphs(before_graph, after_graph, debug=False):
    """
    Compares two room graphs and returns the differences.
    """
    _log_debug_event("INFO", "DiffRoomGraphs", "Comparing room graphs.", debug_enabled=debug)

    before_node_types = {n["node_type"] for n in before_graph.get("nodes", [])}
    after_node_types = {n["node_type"] for n in after_graph.get("nodes", [])}
    
    new_room_types = list(after_node_types - before_node_types)
    survivor_mark_room_added = "survivor_mark_room" in new_room_types
    
    mutation_level_delta = after_graph.get("mutation_level", 0) - before_graph.get("mutation_level", 0)
    
    # Check if graph changed (nodes or connections)
    # Since our builder is deterministic and simplified, we check mutation level and node type changes
    graph_changed = (mutation_level_delta != 0) or (before_node_types != after_node_types)

    diff = {
        "graph_changed": graph_changed,
        "new_room_types": new_room_types,
        "survivor_mark_room_added": survivor_mark_room_added,
        "mutation_level_delta": mutation_level_delta,
        "identity_preserved": after_graph.get("identity_preserved", True),
        "playability_preserved": after_graph.get("playability_preserved", True)
    }
    
    return diff

def make_room_graph_mutation_evidence(floor_record, floor_memory_before, floor_memory_after, debug=False):
    """
    Creates before/after room graph evidence for replay-mutated floors.
    """
    evidence_id = f"room_graph_evidence_{uuid.uuid4().hex[:8]}"
    _log_debug_event("INFO", "MakeEvidence", f"Creating evidence {evidence_id}", debug_enabled=debug)

    if not floor_record or not floor_memory_before or not floor_memory_after:
        return {
            "evidence_id": evidence_id,
            "ok": False,
            "error": {"type": "InvalidInput", "message": "Missing required records for evidence generation."},
            "readable_summary": ["Failed to generate evidence due to missing inputs."]
        }

    graphs_result = make_before_after_room_graphs(floor_record, floor_memory_before, floor_memory_after, debug=debug)
    if not graphs_result["ok"]:
        return {
            "evidence_id": evidence_id,
            "ok": False,
            "error": {"type": "GraphBuildFailure", "message": graphs_result.get("message", "Failed to build room graphs.")},
            "readable_summary": ["Failed to build room graphs for mutation evidence."]
        }

    before_graph = graphs_result["before_graph"]
    after_graph = graphs_result["after_graph"]
    
    diff = diff_room_graphs(before_graph, after_graph, debug=debug)
    
    evidence = {
        "evidence_id": evidence_id,
        "ok": True,
        "floor_id": floor_record.get("floor_id"),
        "before_graph": before_graph,
        "after_graph": after_graph,
        "graph_changed": diff["graph_changed"],
        "new_room_types": diff["new_room_types"],
        "survivor_mark_room_added": diff["survivor_mark_room_added"],
        "mutation_level_delta": diff["mutation_level_delta"],
        "identity_preserved": diff["identity_preserved"],
        "playability_preserved": diff["playability_preserved"],
        "readable_summary": [], # To be populated
        "error": None
    }
    
    evidence["readable_summary"] = summarize_room_graph_mutation_evidence(evidence)
    
    return evidence

def summarize_room_graph_mutation_evidence(evidence):
    """
    Generates a human-readable summary of the room graph mutation.
    """
    summary = []
    
    if evidence.get("graph_changed"):
        summary.append(f"Room graph layout mutated (Level delta: {evidence.get('mutation_level_delta')}).")
    else:
        summary.append("Room graph layout remains structurally identical.")
        
    if evidence.get("survivor_mark_room_added"):
        summary.append("A new survivor mark room has been manifested in the graph.")
        
    if evidence.get("new_room_types") and not evidence.get("survivor_mark_room_added"):
        summary.append(f"New room types detected: {', '.join(evidence.get('new_room_types'))}")
        
    if evidence.get("identity_preserved"):
        summary.append("Floor identity and landmark anchors preserved.")
    else:
        summary.append("WARNING: Floor identity compromised by mutation.")

    if evidence.get("playability_preserved"):
        summary.append("Critical path from entry to exit remains valid.")
    else:
        summary.append("ERROR: Graph playability failed validation.")

    return summary
