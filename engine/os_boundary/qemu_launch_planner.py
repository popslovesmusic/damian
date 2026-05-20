import json
import os

def generate_qemu_launch_plan():
    config_path = "os/kiosk/qemu_config.json"
    
    if not os.path.exists(config_path):
        print("QEMU config missing.")
        return False

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Build the QEMU command (dry-run/plan)
    qemu_cmd = [
        "qemu-system-x86_64",
        "-name", config["vm_name"],
        "-m", str(config["ram_mb"]),
        "-smp", str(config["cpus"]),
        "-drive", f"file={config['drive']['file']},format={config['drive']['format']},if={config['drive']['interface']}",
        "-display", config["display"],
        "-serial", f"{config['serial']['type']}:{config['serial']['path']}",
        "-net", "none" if config["network"]["restrict"] else "user"
    ]

    launch_plan = {
        "vm_name": config["vm_name"],
        "command_string": " ".join(qemu_cmd),
        "safety_checks": [
            "Network restricted to NONE or USER mode only.",
            "No host file passthrough enabled.",
            "Serial output redirected to log file for success verification."
        ],
        "verdict": "PLAN_ONLY"
    }

    output_path = "build/live_os/images/qemu_launch_plan.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(launch_plan, f, indent=2)
    
    print(f"QEMU launch plan generated at {output_path}")
    return True

if __name__ == "__main__":
    generate_qemu_launch_plan()
