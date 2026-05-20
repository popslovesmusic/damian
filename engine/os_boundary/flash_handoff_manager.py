import os
import json
import hashlib
import time

class FlashHandoffManager:
    def __init__(self, boundary_path, device_contract_path):
        with open(boundary_path, 'r') as f:
            self.boundary = json.load(f)
        with open(device_contract_path, 'r') as f:
            self.contract = json.load(f)
        
        self.evidence = {"checks": [], "verdict": "PENDING"}

    def enumerate_removable_devices(self, simulated_devices=None):
        """Simulates read-only device enumeration with strict host protection."""
        # In a real tool, this would parse output from lsblk, diskpart, or similar.
        devices = simulated_devices or [
            {"id": "sda", "vendor": "Samsung", "model": "NVMe SSD", "size": "512G", "is_removable": False, "interface": "nvme"},
            {"id": "sdb", "vendor": "Sandisk", "model": "Cruzer", "size": "32G", "is_removable": True, "interface": "usb"}
        ]
        
        allowed_devices = []
        for dev in devices:
            # Apply Safety Filter
            is_internal = not dev.get("is_removable", True) or dev.get("interface") in ["nvme", "sata"]
            
            if is_internal:
                self.evidence["checks"].append({
                    "check": "Host Disk Filter",
                    "device_id": dev["id"],
                    "status": "REJECTED",
                    "reason": "Internal/System disk detected."
                })
                continue
                
            allowed_devices.append(dev)
            self.evidence["checks"].append({
                "check": "Removable Device Detected",
                "device_id": dev["id"],
                "status": "PASS"
            })
            
        self.evidence["enumerated_devices"] = allowed_devices
        return allowed_devices

    def create_flashing_plan(self, artifact_path, target_device_id):
        """Generates a dry-run flashing plan."""
        # 1. Verify Artifact Integrity
        if not os.path.exists(artifact_path):
            return {"status": "FAIL", "reason": "Artifact missing"}
            
        sha256_hash = hashlib.sha256()
        with open(artifact_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        artifact_hash = sha256_hash.hexdigest()

        plan = {
            "artifact": artifact_path,
            "artifact_hash": artifact_hash,
            "target": target_device_id,
            "actions": [
                {"step": 1, "action": "UNMOUNT_PARTITIONS", "target": target_device_id},
                {"step": 2, "action": "WRITE_IMAGE", "source": artifact_path, "dest": target_device_id, "mode": "STRICT_DD_SIMULATION"},
                {"step": 3, "action": "VERIFY_BLOCKS", "target": target_device_id}
            ],
            "safety_gate": "OPERATOR_CONFIRMATION_REQUIRED"
        }
        
        self.evidence["flashing_plan"] = plan
        self.evidence["checks"].append({"check": "Flashing Plan Generation", "status": "PASS"})
        return plan

    def validate_operator_confirmation(self, device_id, phrase):
        """Validates the explicit confirmation phrase."""
        expected = self.contract["phrase_template"].replace("<DEVICE_ID>", device_id)
        
        status = "PASS" if phrase == expected else "FAIL"
        self.evidence["checks"].append({
            "check": "Operator Acknowledgment Gate",
            "status": status,
            "provided": phrase,
            "expected": expected
        })
        return status == "PASS"

    def get_final_evidence(self):
        if all(c["status"] == "PASS" for c in self.evidence["checks"] if c["check"] != "Host Disk Filter"):
             # Host disk filter rejects are PASS for the safety gate
             self.evidence["verdict"] = "PASS"
        else:
             self.evidence["verdict"] = "FAIL"
        return self.evidence

if __name__ == "__main__":
    # Test stub
    fhm = FlashHandoffManager(
        "engine/os_boundary/contracts/usb_handoff_boundary.json",
        "engine/os_boundary/contracts/usb_device_contract.json"
    )
    
    # 1. Enumerate
    devices = fhm.enumerate_removable_devices()
    print(f"Allowed Devices: {json.dumps(devices, indent=2)}")
    
    # 2. Plan
    # Use the image stub created in STAGE-025 if it exists
    img_path = "build/live_os/images/tower-damian-proto.img"
    if not os.path.exists(img_path):
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'w') as f: f.write("STUB")
        
    plan = fhm.create_flashing_plan(img_path, "sdb")
    
    # 3. Confirm
    success = fhm.validate_operator_confirmation("sdb", "FLASH_TOWER_ARTIFACT_TO_sdb")
    print(f"Confirmation Result: {success}")
    
    print(json.dumps(fhm.get_final_evidence(), indent=2))
