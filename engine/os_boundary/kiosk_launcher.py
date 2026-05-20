import os
import json
import sys
import subprocess
import time
from engine.os_boundary.persistence_manager import PersistenceManager
from engine.os_boundary.launcher_hardener import KioskLauncherHardener

def run_kiosk_launcher():
    print("--- DAMIAN TOWER KIOSK LAUNCHER STARTING ---")
    
    # 1. Initialize Hardener
    os_root = os.environ.get("TOWER_OS_ROOT", "/")
    data_root = os.environ.get("TOWER_DATA_PATH", "/tower/data")
    hardener = KioskLauncherHardener(os_root, data_root)
    
    # 2. Environment Verification
    if not hardener.verify_environment():
        print("ERROR: Environment verification failed.")
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_environment_verification.json")
        return False
    print(f"Verified TOWER_OS at {os_root} and TOWER_DATA at {data_root}")

    # 3. Persistence Path Guard & Initialization
    persistence_paths = ["saves", "logs", "transcripts", "mods", "content_packs", "crash_reports", "state_snapshots", "artifacts"]
    if not hardener.enforce_persistence_guard(persistence_paths):
        print("ERROR: Persistence path guard violation detected.")
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_persistence_guard.json")
        return False
    
    # 4. Explicit Runtime Config Handoff
    runtime_config = hardener.generate_runtime_config()
    
    # 5. Setup Environment Variables for Engine (Mapping from hardener's config)
    os.environ["TOWER_SAVE_DIR"] = runtime_config["save_root"]
    os.environ["TOWER_LOG_DIR"] = runtime_config["log_root"]
    os.environ["TOWER_ARTIFACT_DIR"] = runtime_config["artifact_root"]

    print("Explicit runtime configuration generated and environment variables set.")

    # 6. Engine Handoff
    print("Handing off control to Tower Engine Orchestrator...")
    
    handoff_report = {
        "status": "READY",
        "timestamp": time.time(),
        "runtime_config": runtime_config,
        "hardening_verdict": "PASS"
    }
    
    handoff_log_path = os.path.join(runtime_config["log_root"], "launcher_handoff.json")
    with open(handoff_log_path, 'w') as f:
        json.dump(handoff_report, f, indent=2)
    
    hardener.emit_success_audit("outputs/audits/kiosk_launcher_environment_verification.json")
    
    print(f"Handoff report written to {handoff_log_path}")
    print("--- LAUNCHER COMPLETE, ENGINE RUNNING ---")
    return True

if __name__ == "__main__":
    success = run_kiosk_launcher()
    if not success:
        sys.exit(1)
