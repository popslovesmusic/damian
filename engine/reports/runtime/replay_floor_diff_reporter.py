import os
import json
import sys
import datetime
import uuid

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import json_save_manager (assuming project root is in sys.path)
try:
    from engine.save.runtime import json_save_manager
    _json_save_manager_available = True
except ImportError:
    _json_save_manager_available = False

# Paths to existing schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_FLOOR_MEMORY_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/save/schemas/floor_memory.schema.json")


def _log_debug_event(patch_id, system, severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        event = debug_logger.make_debug_event(patch_id, system, severity, event_type, message, context)
        # Assuming debug_logger.write_debug_event handles its own failures
        debug_logger.write_debug_event(event)
    elif not _debug_logger_available and debug_enabled:
        print(f"WARNING: Debugging is enabled but debug_logger is unavailable. Event: {message}")


def create_structured_error(error_type, message, path="", debug=False):
    """Creates a structured error dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "ERROR", error_type, message, {"path": path}, debug)
    return {"ok": False, "error_type": error_type, "message": message, "path": path}

def create_structured_success(payload, path="", debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "OperationSuccess", "Operation completed successfully.", {"path": path}, debug)
    return {"ok": True, "payload": payload, "path": path}


def snapshot_floor_memory(floor_memory):
    """
    Creates a simplified snapshot of a floor memory record for diffing.
    """
    if not isinstance(floor_memory, dict) or "floor_id" not in floor_memory:
        return create_structured_error("InvalidInput", "Invalid floor_memory provided for snapshot.", debug=False)

    # Convert mutable lists to tuples for consistent hashing/comparison if needed, or just copy
    snapshot = {
        "floor_id": floor_memory.get("floor_id"),
        "visit_count": floor_memory.get("visit_count"),
        "death_count": floor_memory.get("death_count"),
        "victory_count": floor_memory.get("victory_count"),
        "stability": floor_memory.get("stability"),
        "deviation": floor_memory.get("deviation"),
        "mutation_level": floor_memory.get("mutation_level"),
        "known_layout_seed": floor_memory.get("known_layout_seed"),
        "active_mutations": sorted(floor_memory.get("active_mutations", [])), # Sort for consistent comparison
        "discovered_easter_eggs": sorted(floor_memory.get("discovered_easter_eggs", [])),
        "unclaimed_easter_eggs": sorted(floor_memory.get("unclaimed_easter_eggs", [])),
        "residue_history_count": len(floor_memory.get("residue_history", []))
    }
    return create_structured_success(snapshot)


def diff_floor_snapshots(before_snapshot, after_snapshot, debug=False):
    """
    Compares two floor memory snapshots and identifies changes.
    """
    _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "DiffSnapshots", "Diffing floor snapshots.", debug_enabled=debug)

    if not before_snapshot or not after_snapshot:
        return create_structured_error("InvalidInput", "Both before and after snapshots are required for diffing.", debug=debug)
    if before_snapshot.get("floor_id") != after_snapshot.get("floor_id"):
        return create_structured_error("InvalidInput", "Snapshots must be for the same floor_id.", debug=debug)

    diff_data = {
        "mutation_level_delta": after_snapshot.get("mutation_level", 0) - before_snapshot.get("mutation_level", 0),
        "stability_delta": after_snapshot.get("stability", 0.0) - before_snapshot.get("stability", 0.0),
        "deviation_delta": after_snapshot.get("deviation", 0.0) - before_snapshot.get("deviation", 0.0),
        "new_active_mutations": [],
        "new_unclaimed_survivor_marks": [],
        "new_discovered_survivor_marks": [],
        "residue_history_delta": after_snapshot.get("residue_history_count", 0) - before_snapshot.get("residue_history_count", 0)
    }

    # Identify new active mutations
    for mutation in after_snapshot.get("active_mutations", []):
        if mutation not in before_snapshot.get("active_mutations", []):
            diff_data["new_active_mutations"].append(mutation)
    
    # Identify new unclaimed survivor marks
    for mark in after_snapshot.get("unclaimed_easter_eggs", []):
        if mark not in before_snapshot.get("unclaimed_easter_eggs", []):
            diff_data["new_unclaimed_survivor_marks"].append(mark)

    # Identify newly discovered marks (moved from unclaimed to discovered)
    # This is tricky without knowing the full state change or relying on unique mark IDs
    # For MVP, we'll simply report any marks in after.discovered that weren't in before.discovered
    for mark in after_snapshot.get("discovered_easter_eggs", []):
        if mark not in before_snapshot.get("discovered_easter_eggs", []):
            diff_data["new_discovered_survivor_marks"].append(mark)
    
    # Determine if anything significant changed
    changed = (any(v != 0 for k, v in diff_data.items() if "delta" in k) or 
              bool(diff_data["new_active_mutations"]) or 
              bool(diff_data["new_unclaimed_survivor_marks"]) or 
              bool(diff_data["new_discovered_survivor_marks"]))
              
    return create_structured_success({"changed": changed, "diff": diff_data}, debug=debug)


def make_replay_floor_diff_report(before_floor_memory, after_floor_memory, debug=False):
    """
    Compares two floor memory records (before and after replay) and generates a diff report.
    """
    _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "MakeDiffReport", "Generating replay floor diff report.", debug_enabled=debug)

    if not before_floor_memory or not after_floor_memory:
        return create_structured_error("InvalidInput", "Both before and after floor memory records are required.", debug=debug)
    
    if before_floor_memory.get("floor_id") != after_floor_memory.get("floor_id"):
        return create_structured_error("InvalidInput", "Floor memory records must be for the same floor_id.", debug=debug)

    # Create snapshots
    before_snapshot_result = snapshot_floor_memory(before_floor_memory)
    if not before_snapshot_result["ok"]:
        return create_structured_error("SnapshotFailure", before_snapshot_result["message"], debug=debug)
    before_snapshot = before_snapshot_result["payload"]

    after_snapshot_result = snapshot_floor_memory(after_floor_memory)
    if not after_snapshot_result["ok"]:
        return create_structured_error("SnapshotFailure", after_snapshot_result["message"], debug=debug)
    after_snapshot = after_snapshot_result["payload"]

    # Diff snapshots
    diff_result = diff_floor_snapshots(before_snapshot, after_snapshot, debug=debug)
    if not diff_result["ok"]:
        return create_structured_error("DiffFailure", diff_result["message"], debug=debug)
    
    diff_data = diff_result["payload"]["diff"]
    changed = diff_result["payload"]["changed"]

    report_id = f"floor_diff_{uuid.uuid4().hex[:8]}"
    report = {
        "report_id": report_id,
        "ok": True,
        "floor_id": before_floor_memory.get("floor_id"),
        "changed": changed,
        "before": before_snapshot,
        "after": after_snapshot,
        "changes": diff_data,
        "readable_summary": summarize_replay_floor_diff(diff_data)["payload"], # Use summarize_replay_floor_diff
        "error": None
    }
    _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "DiffReportMade", "Replay floor diff report generated.", {"report_id": report_id}, debug)
    return create_structured_success(report, debug=debug)


def write_replay_floor_diff_report(report, output_path, debug=False):
    """
    Writes the replay floor diff report to a JSON file.
    """
    if not _json_save_manager_available:
        return create_structured_error("DependencyError", "json_save_manager is not available.", debug=debug)
    
    _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "WriteDiffReport", f"Writing diff report to {output_path}.", {"path": output_path}, debug)
    result = json_save_manager.save_json(output_path, report, debug=debug)
    if not result["ok"]:
        _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "ERROR", "DiffReportWriteFailure", f"Failed to write diff report to {output_path}: {result['message']}", debug_enabled=debug)
        return create_structured_error("DiffReportWriteFailure", f"Failed to write diff report: {result['message']}", output_path, debug=debug)
    
    return create_structured_success(None, output_path, debug=debug)


def summarize_replay_floor_diff(diff_data, debug=False):
    """
    Generates a human-readable summary of the floor changes.
    """
    _log_debug_event("TOWER-ENGINE-032", "replay_floor_diff_reporter", "INFO", "SummarizeDiff", "Summarizing replay floor diff.", debug_enabled=debug)

    summary_lines = []
    
    # Floor identity preserved statement (conceptual for now)
    summary_lines.append("Floor identity appears preserved (conceptual check).")

    # Mutation level change
    if diff_data["mutation_level_delta"] > 0:
        summary_lines.append(f"Mutation level increased by {diff_data['mutation_level_delta']}.")
    elif diff_data["mutation_level_delta"] < 0:
        summary_lines.append(f"Mutation level decreased by {-diff_data['mutation_level_delta']}.")
    else:
        summary_lines.append("Mutation level remained unchanged.")

    # Active mutations
    if diff_data["new_active_mutations"]:
        summary_lines.append(f"New active mutations: {', '.join(diff_data['new_active_mutations'])}.")

    # Survivor marks
    if diff_data["new_unclaimed_survivor_marks"]:
        summary_lines.append(f"New unclaimed survivor marks detected: {', '.join(diff_data['new_unclaimed_survivor_marks'])}.")
    if diff_data["new_discovered_survivor_marks"]:
        summary_lines.append(f"New discovered survivor marks: {', '.join(diff_data['new_discovered_survivor_marks'])}.")
    
    # Residue history
    if diff_data["residue_history_delta"] > 0:
        summary_lines.append(f"Residue history count increased by {diff_data['residue_history_delta']}.")
    elif diff_data["residue_history_delta"] < 0:
        summary_lines.append(f"Residue history count decreased by {-diff_data['residue_history_delta']}.")

    return create_structured_success(summary_lines, debug=debug)
