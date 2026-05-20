import json
import os
import shutil

def materialize_rootfs_staging():
    plan_path = "outputs/audits/rootfs_materialization_plan.json"
    
    if not os.path.exists(plan_path):
        print("Materialization plan not found. Run planner first.")
        return False

    with open(plan_path, 'r') as f:
        plan = json.load(f)

    staging_root = plan["staging_root"]
    
    # Cleanup old staging
    if os.path.exists(staging_root):
        shutil.rmtree(staging_root)
    
    os.makedirs(staging_root, exist_ok=True)

    print(f"Materializing RootFS to {staging_root}...")

    for step in plan["steps"]:
        action = step["action"]
        path = step["path"] if "path" in step else step["target"]
        
        if action == "mkdir":
            os.makedirs(path, exist_ok=True)
        elif action in ["stage_file", "stage_content"]:
            source = step["source"]
            target = step["target"]
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(source, target)
            print(f"  Staged: {source} -> {target}")

    print("RootFS materialization complete.")
    return True

if __name__ == "__main__":
    materialize_rootfs_staging()
