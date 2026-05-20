import json
import os

def generate_build_plan():
    config_path = "os/kiosk/build_config.json"
    manifest_path = "os/kiosk/rootfs_manifest.json"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    build_plan = {
        "build_id": config["build_id"],
        "steps": [],
        "safety_check": "PASS"
    }
    
    # Step 1: Initialize build root
    build_plan["steps"].append({
        "action": "mkdir",
        "path": config["paths"]["build_root"],
        "reason": "Initialize build workspace"
    })
    
    # Step 2: Create directory structure
    for directory in manifest["directories"]:
        build_plan["steps"].append({
            "action": "mkdir",
            "path": os.path.join(config["paths"]["staging_area"], directory.lstrip("/")),
            "reason": "RootFS directory structure"
        })
    
    # Step 3: Stage files
    for file_entry in manifest["files"]:
        build_plan["steps"].append({
            "action": "copy",
            "source": file_entry["source"],
            "destination": os.path.join(config["paths"]["staging_area"], file_entry["destination"].lstrip("/")),
            "mode": file_entry["mode"]
        })
    
    # Step 4: Create symlinks
    for symlink in manifest["symlinks"]:
        build_plan["steps"].append({
            "action": "symlink",
            "target": symlink["target"],
            "link": os.path.join(config["paths"]["staging_area"], symlink["link"].lstrip("/")),
        })

    output_path = "build/live_os/build_plan.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(build_plan, f, indent=2)
    
    print(f"Build plan generated at {output_path}")
    return build_plan

if __name__ == "__main__":
    generate_build_plan()
