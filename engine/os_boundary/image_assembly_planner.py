import json
import os

def generate_assembly_plan():
    config_path = "os/kiosk/image_config.json"
    build_plan_path = "build/live_os/build_plan.json"
    
    if not os.path.exists(config_path) or not os.path.exists(build_plan_path):
        print("Required configs missing.")
        return False

    with open(config_path, 'r') as f:
        image_config = json.load(f)
    
    assembly_plan = {
        "image_id": image_config["image_id"],
        "assembly_steps": [
            {
                "step": 1,
                "action": "calculate_required_size",
                "details": "Aggregate size of staged RootFS and expected TOWER_DATA overhead."
            },
            {
                "step": 2,
                "action": "create_empty_sparse_file",
                "target": os.path.join(image_config["output"]["directory"], image_config["output"]["filename"]),
                "safety": "Ensures no host disk sectors are overwritten until explicitly mapped."
            },
            {
                "step": 3,
                "action": "map_partitions",
                "layout": [
                    {"label": "TOWER_OS", "type": "squashfs", "source": "build/live_os/staging"},
                    {"label": "TOWER_DATA", "type": "ext4", "source": "empty"}
                ]
            },
            {
                "step": 4,
                "action": "inject_bootloader_config",
                "params": image_config["boot_params"]
            }
        ],
        "verdict": "PLAN_ONLY"
    }

    output_path = "build/live_os/images/assembly_plan.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(assembly_plan, f, indent=2)
    
    print(f"Assembly plan generated at {output_path}")
    return True

if __name__ == "__main__":
    generate_assembly_plan()
