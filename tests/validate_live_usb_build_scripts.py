import json
import os

def run_dry_run_validation():
    audit_results = {
        "patch_id": "STAGE-022",
        "verdict": "FAIL",
        "checks": []
    }

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    plan_path = os.path.join(project_root, "build/live_os/build_plan.json")
    
    if not os.path.exists(plan_path):
        audit_results["checks"].append({"check": "Build plan exists", "status": "FAIL", "reason": "build_plan.json not found. Run generator first."})
        return audit_results

    with open(plan_path, 'r') as f:
        plan = json.load(f)

    audit_results["checks"].append({"check": "Build plan exists", "status": "PASS"})

    # Check: No destructive disk operations
    destructive_check = {"check": "No destructive disk operations in plan", "status": "PASS"}
    for step in plan["steps"]:
        action = step.get("action", "").lower()
        if any(keyword in action for keyword in ["format", "partition", "fdisk", "parted", "mkfs"]):
            destructive_check["status"] = "FAIL"
            destructive_check["reason"] = f"Destructive action '{action}' found in plan step."
            break
    audit_results["checks"].append(destructive_check)

    # Check: All write targets are inside project or explicit build dir
    path_boundary_check = {"check": "All write targets are within project/build boundaries", "status": "PASS"}
    for step in plan["steps"]:
        path = step.get("path", "")
        if not path:
            path = step.get("destination", "")
        
        if path:
            # Normalize path
            norm_path = os.path.normpath(path)
            # In our proto, everything should be under 'build/' or 'outputs/' or 'os/'
            if not (norm_path.startswith("build") or norm_path.startswith("outputs") or norm_path.startswith("os")):
                 path_boundary_check["status"] = "FAIL"
                 path_boundary_check["reason"] = f"Path '{norm_path}' is outside permitted build boundaries."
                 break
    audit_results["checks"].append(path_boundary_check)

    # Check: Required templates exist
    templates_check = {"check": "Required templates exist in project", "status": "PASS"}
    required_templates = [
        "os/kiosk/templates/tower-kiosk.service",
        "os/kiosk/templates/tower-data.mount"
    ]
    for template in required_templates:
        if not os.path.exists(os.path.join(project_root, template)):
            templates_check["status"] = "FAIL"
            templates_check["reason"] = f"Template '{template}' missing."
            break
    audit_results["checks"].append(templates_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "live_usb_dry_run_report.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    print(f"Dry-run report written to {audit_file_path}")
    return audit_results

if __name__ == "__main__":
    run_dry_run_validation()
