import os
import json
import sys
import shutil

class PersistenceManager:
    def __init__(self, mount_point, partition_label="TOWER_DATA"):
        self.mount_point = mount_point
        self.partition_label = partition_label
        self.evidence = {
            "partition_detected": False,
            "mount_validated": False,
            "directories_initialized": [],
            "write_probe_success": False,
            "errors": []
        }

    def detect_partition(self, simulated=False):
        """Simulates or performs partition detection."""
        print(f"Probing for partition: {self.partition_label}")
        if simulated:
            # In a real system, we'd use blkid or similar
            self.evidence["partition_detected"] = os.path.exists(self.mount_point)
        else:
            # For this stage, we assume the mount point is the proxy for the partition
            self.evidence["partition_detected"] = os.path.exists(self.mount_point)
        
        if not self.evidence["partition_detected"]:
            self.evidence["errors"].append(f"Partition {self.partition_label} not found at {self.mount_point}")
        return self.evidence["partition_detected"]

    def validate_mount(self):
        """Verifies the mount point exists and is writable."""
        if os.path.exists(self.mount_point):
            self.evidence["mount_validated"] = True
            # Check if writable
            if not os.access(self.mount_point, os.W_OK):
                self.evidence["mount_validated"] = False
                self.evidence["errors"].append(f"Mount point {self.mount_point} is not writable.")
        else:
            self.evidence["errors"].append(f"Mount point {self.mount_point} does not exist.")
        return self.evidence["mount_validated"]

    def initialize_structure(self, directories):
        """Creates the required directory structure if missing."""
        if not self.evidence["mount_validated"]:
            return False

        for subdir in directories:
            path = os.path.join(self.mount_point, subdir)
            try:
                os.makedirs(path, exist_ok=True)
                self.evidence["directories_initialized"].append(subdir)
            except Exception as e:
                self.evidence["errors"].append(f"Failed to create directory {subdir}: {str(e)}")
        
        # Create probe marker
        try:
            with open(os.path.join(self.mount_point, ".tower_data_marker"), 'w') as f:
                f.write("TOWER_DATA_PROBE_SUCCESS")
        except Exception as e:
            self.evidence["errors"].append(f"Failed to create probe marker: {str(e)}")

        return len(self.evidence["directories_initialized"]) == len(directories)

    def run_write_probe(self, filename, content):
        """Verifies that a file can be written and read back from the persistent partition."""
        if not self.evidence["mount_validated"]:
            return False

        probe_path = os.path.join(self.mount_point, filename)
        try:
            with open(probe_path, 'w') as f:
                json.dump(content, f)
            
            with open(probe_path, 'r') as f:
                read_content = json.load(f)
            
            if read_content == content:
                self.evidence["write_probe_success"] = True
            else:
                self.evidence["errors"].append("Write probe content mismatch.")
        except Exception as e:
            self.evidence["errors"].append(f"Write probe failed: {str(e)}")
        
        return self.evidence["write_probe_success"]

    def get_audit_report(self):
        return self.evidence

if __name__ == "__main__":
    # Internal test/stub runner
    mount = "build/test_tower_data"
    os.makedirs(mount, exist_ok=True)
    
    pm = PersistenceManager(mount)
    pm.detect_partition()
    pm.validate_mount()
    pm.initialize_structure([
        "saves/", "logs/", "transcripts/", "mods/", "content_packs/", "crash_reports/", "state_snapshots/"
    ])
    pm.run_write_probe("runtime_write_probe.json", {"status": "success", "probe": "STAGE-029"})
    
    print(json.dumps(pm.get_audit_report(), indent=2))
