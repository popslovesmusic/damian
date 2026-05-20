import json
import os

def generate_materialization_plan():
    manifest_path = "os/kiosk/rootfs_package_manifest.json"
    boundary_path = "engine/os_boundary/contracts/rootfs_materialization_boundary.json"
    
    if not os.path.exists(manifest_path) or not os.path.exists(boundary_path):
        print("Required configs missing.")
        return False

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    with open(boundary_path, 'r') as f:
        boundary = json.load(f)

    staging_root = boundary["staged_layout"]["base_path"]

    plan = {
        "package_id": manifest["package_id"],
        "staging_root": staging_root,
        "steps": []
    }

    # Step 1: Create subdirs
    for subdir in boundary["staged_layout"]["required_subdirs"]:
        plan["steps"].append({
            "action": "mkdir",
            "path": os.path.join(staging_root, subdir),
            "reason": "RootFS layout compliance"
        })

    # Step 2: Stage components
    for component in manifest["engine_components"]:
        plan["steps"].append({
            "action": "stage_file",
            "name": component["name"],
            "source": component["source"],
            "target": os.path.join(staging_root, component["target"].lstrip("/")),
            "mode": component["mode"]
        })

    # Step 3: Stage content
    for content_path in manifest["verified_content"]:
        plan["steps"].append({
            "action": "stage_content",
            "source": content_path,
            "target": os.path.join(staging_root, "usr/share/damian/", content_path),
            "reason": "Verified content inclusion"
        })

    output_path = "outputs/audits/rootfs_materialization_plan.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print(f"Materialization plan generated at {output_path}")
    return True

if __name__ == "__main__":
    generate_materialization_plan()
