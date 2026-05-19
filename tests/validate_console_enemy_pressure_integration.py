import os
import json
import subprocess
import sys

def run_console_pressure_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-049",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 1. Check if design doc exists
    doc_path = os.path.join(project_root, "docs/design/console/console_combat_enemy_pressure.md")
    audit_results["checks"].append({
        "check": "Design document exists",
        "status": "PASS" if os.path.exists(doc_path) else "FAIL"
    })

    # 2. Check if test file exists
    test_file_path = os.path.join(project_root, "engine/console/runtime/tests/test_mvp_text_console_enemy_pressure.py")
    audit_results["checks"].append({
        "check": "Integration test file exists",
        "status": "PASS" if os.path.exists(test_file_path) else "FAIL"
    })

    # 3. Check for enemy_pressure_selector import in mvp_text_console.py
    console_path = os.path.join(project_root, "engine/console/runtime/mvp_text_console.py")
    try:
        with open(console_path, 'r') as f:
            content = f.read()
            import_check = "from engine.enemies.runtime import enemy_pressure_selector" in content
            audit_results["checks"].append({
                "check": "enemy_pressure_selector imported in mvp_text_console.py",
                "status": "PASS" if import_check else "FAIL"
            })
            
            # Check for selection calls
            select_call_check = "enemy_pressure_selector.select_enemy_archetype" in content
            build_call_check = "enemy_pressure_selector.build_enemy_pressure_profile" in content
            audit_results["checks"].append({
                "check": "combat command calls enemy_pressure_selector",
                "status": "PASS" if (select_call_check and build_call_check) else "FAIL"
            })
            
            # Check for inclusion in combat session
            session_check = "enemy_pressure_profile=pressure_profile" in content
            audit_results["checks"].append({
                "check": "combat command includes profile in session",
                "status": "PASS" if session_check else "FAIL"
            })
            
            # Check for payload additions
            payload_checks = [
                '"enemy_archetype_id": resolution_result.get("enemy_archetype_id")',
                '"enemy_adaptation_reasoning": resolution_result.get("enemy_adaptation_reasoning", [])',
                '"enemy_pressure_profile_used": resolution_result.get("enemy_pressure_profile_used", False)'
            ]
            payload_status = "PASS" if all(pc in content for pc in payload_checks) else "FAIL"
            audit_results["checks"].append({
                "check": "combat command payload includes required fields",
                "status": payload_status
            })
    except Exception as e:
        audit_results["checks"].append({"check": "Read mvp_text_console.py", "status": "FAIL", "reason": str(e)})

    # 4. Run tests
    try:
        test_result = subprocess.run(
            ["py", "-m", "pytest", "engine/console/runtime/tests/test_mvp_text_console_enemy_pressure.py"],
            capture_output=True, text=True
        )
        audit_results["checks"].append({
            "check": "Console enemy pressure integration tests pass",
            "status": "PASS" if test_result.returncode == 0 else "FAIL",
            "reason": test_result.stdout if test_result.returncode != 0 else None
        })
    except Exception as e:
        audit_results["checks"].append({"check": "Run integration tests", "status": "FAIL", "reason": str(e)})

    # 5. Run existing console tests to ensure no regressions
    try:
        # We'll just check if they PASS
        reg_test_files = [
            "engine/console/runtime/tests/test_mvp_text_console.py",
            "engine/console/runtime/tests/test_mvp_text_console_combat_command.py"
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

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    # Write audit file
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_049_console_enemy_pressure_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    # Write result file
    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_049_console_enemy_pressure_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_console_pressure_audit()
    print(json.dumps(audit, indent=2))
