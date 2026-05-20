import os
import json
import sys
import time

class KioskLauncherHardener:
    def __init__(self, os_root, data_root):
        self.os_root = os_root
        self.data_root = data_root
        self.audit_log = {
            "timestamp": time.time(),
            "verifications": {},
            "verdict": "PENDING",
            "errors": []
        }

    def verify_environment(self):
        """Deep verification of the OS and Data environment."""
        # 1. Verify OS Root (Read-only check)
        # In a real system, we'd check mount flags. For prototype, we check path existence.
        self.audit_log["verifications"]["os_root_detected"] = os.path.exists(self.os_root)
        
        # 2. Verify Data Root (Writable check)
        self.audit_log["verifications"]["data_root_detected"] = os.path.exists(self.data_root)
        if self.audit_log["verifications"]["data_root_detected"]:
            self.audit_log["verifications"]["data_root_writable"] = os.access(self.data_root, os.W_OK)
        else:
            self.audit_log["verifications"]["data_root_writable"] = False
            self.audit_log["errors"].append("TOWER_DATA root not found.")

        return all([
            self.audit_log["verifications"].get("os_root_detected"),
            self.audit_log["verifications"].get("data_root_writable")
        ])

    def enforce_persistence_guard(self, sub_paths):
        """Ensures all required persistence paths are strictly within TOWER_DATA."""
        guard_results = {}
        for sp in sub_paths:
            full_path = os.path.join(self.data_root, sp)
            # Normalization check to prevent traversal escapes
            norm_path = os.path.normpath(full_path)
            if not norm_path.startswith(os.path.normpath(self.data_root)):
                self.audit_log["errors"].append(f"Persistence guard violation: {sp} attempts to escape {self.data_root}")
                guard_results[sp] = "VIOLATION"
            else:
                os.makedirs(norm_path, exist_ok=True)
                guard_results[sp] = "SAFE"
        
        self.audit_log["verifications"]["persistence_guard"] = guard_results
        return all(v == "SAFE" for v in guard_results.values())

    def generate_runtime_config(self, engine_mode="kiosk"):
        """Generates the explicit runtime configuration for the Tower Engine."""
        config = {
            "engine_mode": engine_mode,
            "content_pack_root": os.path.join(self.os_root, "usr/share/damian"),
            "save_root": os.path.join(self.data_root, "saves"),
            "log_root": os.path.join(self.data_root, "logs"),
            "artifact_root": os.path.join(self.data_root, "artifacts"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.audit_log["runtime_config"] = config
        return config

    def emit_failure_audit(self, output_path):
        """Writes the failure audit report."""
        self.audit_log["verdict"] = "FAIL"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"Failure audit emitted to {output_path}")

    def emit_success_audit(self, output_path):
        """Writes the success audit report."""
        self.audit_log["verdict"] = "PASS"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"Success audit emitted to {output_path}")

if __name__ == "__main__":
    # Test stub
    os_root = "build/live_os/rootfs_staging"
    data_root = "build/runtime_persistence_test"
    
    hardener = KioskLauncherHardener(os_root, data_root)
    if hardener.verify_environment():
        if hardener.enforce_persistence_guard(["saves", "logs", "artifacts"]):
            config = hardener.generate_runtime_config()
            hardener.emit_success_audit("outputs/audits/kiosk_launcher_runtime_hardening_test.json")
        else:
            hardener.emit_failure_audit("outputs/audits/kiosk_launcher_runtime_hardening_test.json")
    else:
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_runtime_hardening_test.json")
