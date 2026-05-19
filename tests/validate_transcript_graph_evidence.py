import os
import json
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from engine.console.reports import console_transcript_reporter

def run_transcript_graph_evidence_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-045",
        "verdict": "FAIL",
        "checks": []
    }

    # Paths
    reporter_path = os.path.join(project_root, "engine/console/reports/console_transcript_reporter.py")
    test_path = os.path.join(project_root, "engine/console/reports/tests/test_console_transcript_graph_evidence.py")
    
    # Check 1: console_transcript_reporter.py updated
    exists_check = {"check": "console_transcript_reporter.py updated", "status": "PASS"}
    if not os.path.exists(reporter_path):
        exists_check["status"] = "FAIL"
        exists_check["reason"] = "File not found"
    else:
        with open(reporter_path, 'r') as f:
            content = f.read()
            if "room_graph_evidence_observed" not in content or "TOWER-ENGINE-045" not in content:
                exists_check["status"] = "FAIL"
                exists_check["reason"] = "room_graph_evidence integration or patch_id update missing"
    audit_results["checks"].append(exists_check)

    # Check 2: Graph evidence transcript test file exists
    test_exists_check = {"check": "Graph evidence transcript test file exists", "status": "PASS"}
    if not os.path.exists(test_path):
        test_exists_check["status"] = "FAIL"
        test_exists_check["reason"] = "Test file not found"
    audit_results["checks"].append(test_exists_check)

    # Functional Checks using the transcript reporter
    test_dir = "test_temp_audit_transcript_graph_evidence"
    # Write to project root outputs dir for the final artifact
    output_dir = os.path.join(project_root, "outputs/console_transcripts")
    os.makedirs(test_dir, exist_ok=True)
    
    # Setup default paths from orchestrator
    from engine.console.runtime import mvp_text_console
    paths = mvp_text_console.mvp_startup_orchestrator.make_default_runtime_paths(base_save_dir=test_dir)
    
    # Initialize valid state files
    with open(paths["tower_state"], 'w') as f:
        json.dump({
            "tower_state_id": "audit_tower",
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
        
    with open(paths["player_progression"], 'w') as f:
        json.dump({
            "player_id": "audit_player",
            "profile_id": "profile_audit",
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

    commands = ["combat dangerous", "diff", "quit"]
    transcript = console_transcript_reporter.run_console_transcript(
        commands, paths=paths, output_dir=output_dir, transcript_id="graph_combat_validation"
    )

    if not transcript["ok"]:
        audit_results["checks"].append({"check": "Transcript execution", "status": "FAIL", "reason": f"Execution failed: {transcript.get('errors')}"})
    else:
        # Check 3: combat observations
        combat_check = {"check": "Transcript captures combat sessions and outcomes", "status": "PASS"}
        if transcript["combat_sessions_observed"] != 1 or "DEFEAT_DROP" not in transcript["combat_outcomes_observed"]:
            combat_check["status"] = "FAIL"
            combat_check["reason"] = f"Combat observation failed: {transcript['combat_sessions_observed']} sessions, {transcript['combat_outcomes_observed']} outcomes"
        audit_results["checks"].append(combat_check)

        # Check 4: mutation observations
        mutation_check = {"check": "Transcript captures mutation after combat", "status": "PASS"}
        if not transcript["mutation_after_combat_observed"] or not transcript["mutation_observed"]:
            mutation_check["status"] = "FAIL"
            mutation_check["reason"] = "Mutation observation failed"
        audit_results["checks"].append(mutation_check)

        # Check 5: room graph evidence observed
        rg_check = {"check": "Transcript captures room_graph_evidence_observed = true", "status": "PASS"}
        if not transcript.get("room_graph_evidence_observed"):
            rg_check["status"] = "FAIL"
            rg_check["reason"] = "room_graph_evidence_observed is False"
        audit_results["checks"].append(rg_check)

        # Check 6: room graph changes observed
        changes_check = {"check": "Transcript captures room_graph_changes_observed >= 1", "status": "PASS"}
        if transcript.get("room_graph_changes_observed", 0) < 1:
            changes_check["status"] = "FAIL"
            changes_check["reason"] = f"Changes observed: {transcript.get('room_graph_changes_observed')}"
        audit_results["checks"].append(changes_check)

        # Check 7: survivor mark rooms observed
        marks_check = {"check": "Transcript captures survivor_mark_rooms_observed >= 1", "status": "PASS"}
        if transcript.get("survivor_mark_rooms_observed", 0) < 1:
            marks_check["status"] = "FAIL"
            marks_check["reason"] = f"Mark rooms observed: {transcript.get('survivor_mark_rooms_observed')}"
        audit_results["checks"].append(marks_check)

        # Check 8: graph diff summaries
        summary_check = {"check": "Transcript captures non-empty graph_diff_summaries", "status": "PASS"}
        if not transcript.get("graph_diff_summaries"):
            summary_check["status"] = "FAIL"
            summary_check["reason"] = "graph_diff_summaries is empty"
        audit_results["checks"].append(summary_check)

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    write_results(audit_results)
    return audit_results

def write_results(audit_results):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_045_transcript_graph_evidence_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_045_transcript_graph_evidence_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_transcript_graph_evidence_audit()
    print(json.dumps(audit, indent=2))
