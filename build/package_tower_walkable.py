import os
import shutil
import json

def package_prototype():
    # Load configuration
    with open("build/package_contract.json", "r") as f:
        contract = json.load(f)
    with open("build/package_manifest_rules.json", "r") as f:
        manifest = json.load(f)
        
    dist_dir = contract["dist_dir"]
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Copy files based on manifest
    for item in manifest["include"]:
        if os.path.isdir(item):
            shutil.copytree(item, os.path.join(dist_dir, item))
        else:
            shutil.copy2(item, dist_dir)
            
    # Create bat scripts
    with open(os.path.join(dist_dir, "run_tower.bat"), "w") as f:
        f.write("@echo off\npython run_tower_windowed.py\npause")
    with open(os.path.join(dist_dir, "run_tower_debug.bat"), "w") as f:
        f.write("@echo off\npython run_tower_windowed.py\npause")

    # Create ps1 scripts
    with open(os.path.join(dist_dir, "run_tower.ps1"), "w") as f:
        f.write("python run_tower_windowed.py")
    with open(os.path.join(dist_dir, "run_tower_debug.ps1"), "w") as f:
        f.write("python run_tower_windowed.py")
        
    print(f"Prototype packaged to {dist_dir}")

if __name__ == "__main__":
    package_prototype()
