import os
import json
import subprocess
import sys

def run_loot_stub_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-052",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Check if files exist
    files_to_check = [
        "engine/loot/runtime/mvp_loot_event_stub.py",
        "engine/loot/runtime/tests/test_mvp_loot_event_stub.py",
        "engine/loot/contracts/loot_event.schema.json",
        "docs/design/loot/mvp_loot_event_stub.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Check for required functions in mvp_loot_event_stub.py
    from engine.loot.runtime import mvp_loot_event_stub
    required_functions = [
        "make_loot_event",
        "make_combat_loot_event",
        "make_survivor_mark_loot_event",
        "validate_loot_event",
        "summarize_loot_event"
    ]
    for func_name in required_functions:
        audit_results["checks"].append({
            "check": f"Function exists: {func_name}",
            "status": "PASS" if hasattr(mvp_loot_event_stub, func_name) else "FAIL"
        })

    # 3. Run unit tests
    try:
        test_result = subprocess.run(
            ["py", "-m", "pytest", "engine/loot/runtime/tests/test_mvp_loot_event_stub.py"],
            capture_output=True, text=True
        )
        audit_results["checks"].append({
            "check": "Loot stub unit tests pass",
            "status": "PASS" if test_result.returncode == 0 else "FAIL",
            "reason": test_result.stdout if test_result.returncode != 0 else None
        })
    except Exception as e:
        audit_results["checks"].append({"check": "Run unit tests", "status": "FAIL", "reason": str(e)})

    # 4. Verify loot values for VICTORY_ASCEND
    victory_loot = mvp_loot_event_stub.make_combat_loot_event(1, outcome='VICTORY_ASCEND')
    if victory_loot["ok"]:
        payload = victory_loot["payload"]
        gold_ok = payload["rewards"]["gold"] == 10000
        sink_ok = "resource_sink_pressure" in payload
        flags_ok = all(v is False for v in payload["bounded_reward_flags"].values())
        audit_results["checks"].append({
            "check": "VICTORY_ASCEND rewards and flags are correct",
            "status": "PASS" if (gold_ok and sink_ok and flags_ok) else "FAIL"
        })
    else:
        audit_results["checks"].append({"check": "Verify victory rewards", "status": "FAIL", "reason": "make_combat_loot_event failed"})

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    # Write audit file
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_052_loot_event_stub_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    # Write result file
    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_052_loot_event_stub_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_loot_stub_audit()
    print(json.dumps(audit, indent=2))
