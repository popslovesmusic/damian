import os
import json
import subprocess
import sys

def run_transcript_inventory_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-065",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Check if design doc exists
    doc_path = os.path.join(project_root, "docs/design/console/console_transcript_inventory_evidence.md")
    audit_results["checks"].append({
        "check": "Design document exists",
        "status": "PASS" if os.path.exists(doc_path) else "FAIL"
    })

    # 2. Check if test file exists
    test_file_path = os.path.join(project_root, "engine/console/reports/tests/test_console_transcript_inventory_evidence.py")
    audit_results["checks"].append({
        "check": "Integration test file exists",
        "status": "PASS" if os.path.exists(test_file_path) else "FAIL"
    })

    # 3. Check for new fields in console_transcript_reporter.py
    reporter_path = os.path.join(project_root, "engine/console/reports/console_transcript_reporter.py")
    try:
        with open(reporter_path, 'r') as f:
            content = f.read()
            required_fields = [
                "inventory_transactions_observed",
                "inventory_applications_observed",
                "inventory_failures_observed",
                "total_gold_added_to_inventory",
                "items_added_to_inventory",
                "items_deducted_from_inventory",
                "capacity_pressure_observed",
                "inventory_summaries"
            ]
            fields_check = all(rf in content for rf in required_fields)
            audit_results["checks"].append({
                "check": "Required transcript fields added to reporter",
                "status": "PASS" if fields_check else "FAIL"
            })
            
            # Check for patch_id update
            patch_check = '"patch_id": "TOWER-ENGINE-065"' in content
            audit_results["checks"].append({
                "check": "patch_id updated to TOWER-ENGINE-065",
                "status": "PASS" if patch_check else "FAIL"
            })
    except Exception as e:
        audit_results["checks"].append({"check": "Read console_transcript_reporter.py", "status": "FAIL", "reason": str(e)})

    # 4. Run new integration tests
    try:
        test_result = subprocess.run(
            ["py", "-m", "pytest", "engine/console/reports/tests/test_console_transcript_inventory_evidence.py"],
            capture_output=True, text=True
        )
        audit_results["checks"].append({
            "check": "Console transcript inventory evidence integration tests pass",
            "status": "PASS" if test_result.returncode == 0 else "FAIL",
            "reason": test_result.stdout if test_result.returncode != 0 else None
        })
    except Exception as e:
        audit_results["checks"].append({"check": "Run integration tests", "status": "FAIL", "reason": str(e)})

    # 5. Run existing transcript tests to ensure no regressions
    try:
        reg_test_files = [
            "engine/console/reports/tests/test_console_transcript_reporter.py",
            "engine/console/reports/tests/test_console_transcript_combat_reporting.py",
            "engine/console/reports/tests/test_console_transcript_graph_evidence.py",
            "engine/console/reports/tests/test_console_transcript_enemy_pressure.py",
            "engine/console/reports/tests/test_console_transcript_loot_evidence.py"
        ]
        for tf in reg_test_files:
             if os.path.exists(os.path.join(project_root, tf)):
                reg_result = subprocess.run(["py", "-m", "pytest", tf], capture_output=True, text=True)
                audit_results["checks"].append({
                    "check": f"Regression test {tf} passes",
                    "status": "PASS" if reg_result.returncode == 0 else "FAIL"
                })
    except Exception as e:
         audit_results["checks"].append({"check": "Run regression tests", "status": "FAIL", "reason": str(e)})

    # 6. Generate validation transcript
    try:
        from engine.console.reports import console_transcript_reporter
        transcript = console_transcript_reporter.run_console_transcript(
            ["combat safe"], 
            debug=True, 
            transcript_id="inventory_evidence_validation"
        )
        
        # Verify file existence
        transcript_path = os.path.join(project_root, "outputs/console_transcripts/tower_engine_065_inventory_evidence_console_transcript.json")
        audit_results["checks"].append({
            "check": "Validation transcript generated",
            "status": "PASS" if os.path.exists(transcript_path) else "FAIL"
        })
        
        # Verify transcript content
        if os.path.exists(transcript_path):
            with open(transcript_path, 'r') as f:
                data = json.load(f)
                content_ok = (
                    data.get("inventory_transactions_observed", 0) >= 1 and
                    data.get("total_gold_added_to_inventory", 0) >= 10000 and
                    data.get("inventory_applications_observed", 0) >= 1
                )
                audit_results["checks"].append({
                    "check": "Validation transcript contains inventory evidence",
                    "status": "PASS" if content_ok else "FAIL"
                })
    except Exception as e:
        audit_results["checks"].append({"check": "Generate validation transcript", "status": "FAIL", "reason": str(e)})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    # Write audit file
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_065_transcript_inventory_evidence_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    # Write result file
    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_065_transcript_inventory_evidence_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_transcript_inventory_audit()
    print(json.dumps(audit, indent=2))
