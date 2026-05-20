import os
import json
import subprocess
import sys

def run_potion_command_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-066",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 1. Check Files
    files_to_check = [
        "engine/console/runtime/tests/test_mvp_text_console_consumables.py",
        "docs/design/console/console_consumable_drain_command.md"
    ]
    for f in files_to_check:
        audit_results["checks"].append({
            "check": f"File exists: {f}",
            "status": "PASS" if os.path.exists(os.path.join(project_root, f)) else "FAIL"
        })

    # 2. Check Registry
    registry_path = os.path.join(project_root, "engine/console/console_command_registry.json")
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            registry = json.load(f)
            has_potion = any(cmd.get("command") == "potion" for cmd in registry.get("commands", []))
            audit_results["checks"].append({"check": "Console command registry includes potion", "status": "PASS" if has_potion else "FAIL"})

    # 3. Check for handler in mvp_text_console.py
    console_path = os.path.join(project_root, "engine/console/runtime/mvp_text_console.py")
    try:
        with open(console_path, 'r') as f:
            content = f.read()
            handler_check = "def _handle_potion" in content
            dispatch_check = 'elif command == "potion":' in content
            trans_check = "inventory_transaction_stub.consume_inventory_item" in content
            
            audit_results["checks"].append({"check": "_handle_potion implemented", "status": "PASS" if handler_check else "FAIL"})
            audit_results["checks"].append({"check": "potion command dispatched", "status": "PASS" if dispatch_check else "FAIL"})
            audit_results["checks"].append({"check": "potion uses inventory stub", "status": "PASS" if trans_check else "FAIL"})
    except Exception as e:
        audit_results["checks"].append({"check": "Read console code", "status": "FAIL", "reason": str(e)})

    # 4. Run unit tests
    try:
        test_result = subprocess.run(
            ["py", "-m", "pytest", "engine/console/runtime/tests/test_mvp_text_console_consumables.py"],
            capture_output=True, text=True
        )
        audit_results["checks"].append({
            "check": "Potion command unit tests pass",
            "status": "PASS" if test_result.returncode == 0 else "FAIL",
            "reason": test_result.stdout if test_result.returncode != 0 else None
        })
    except Exception as e:
        audit_results["checks"].append({"check": "Run unit tests", "status": "FAIL", "reason": str(e)})

    # 5. Run regression tests
    try:
        reg_test_files = [
            "engine/console/runtime/tests/test_mvp_text_console.py",
            "engine/console/runtime/tests/test_mvp_text_console_combat_command.py",
            "engine/console/runtime/tests/test_mvp_text_console_enemy_pressure.py",
            "engine/console/runtime/tests/test_mvp_text_console_combat_loot.py",
            "engine/console/runtime/tests/test_mvp_text_console_equipment_pressure.py"
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

    # Write audit file
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_066_consumable_drain_command_audit.json")
    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    # Write result file
    result_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(result_dir, exist_ok=True)
    result_file_path = os.path.join(result_dir, "tower_engine_066_consumable_drain_command_result.json")
    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

    print(f"Audit results written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    audit = run_potion_command_audit()
    print(json.dumps(audit, indent=2))
