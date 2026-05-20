import os
import json
import sys
import subprocess
import time
from engine.os_boundary.persistence_manager import PersistenceManager

def run_kiosk_launcher():
    print("--- DAMIAN TOWER KIOSK LAUNCHER STARTING ---")
    
    # 1. Verify Environment and Persistence
    tower_data_path = os.environ.get("TOWER_DATA_PATH", "mnt/tower_data")
    pm = PersistenceManager(tower_data_path)
    
    if not pm.detect_partition():
        print(f"ERROR: Persistent data partition not found at {tower_data_path}")
        return False

    if not pm.validate_mount():
        print(f"ERROR: Persistent mount at {tower_data_path} is not valid or writable.")
        return False

    print(f"Verified TOWER_DATA at {tower_data_path}")

    # 2. Setup Runtime Folders
    required_folders = [
        "saves/", "logs/", "transcripts/", "mods/", 
        "content_packs/", "crash_reports/", "state_snapshots/"
    ]
    if not pm.initialize_structure(required_folders):
        print("ERROR: Failed to initialize persistent folder structure.")
        return False

    # 3. Runtime Write Verification
    if not pm.run_write_probe("runtime_write_probe.json", {"status": "success", "probe": "STAGE-029"}):
        print("ERROR: Runtime write verification failed on persistent partition.")
        return False

    # 4. Setup Environment Variables for Engine
    os.environ["TOWER_SAVE_DIR"] = os.path.join(tower_data_path, "saves")
    os.environ["TOWER_LOG_DIR"] = os.path.join(tower_data_path, "logs")
    os.environ["TOWER_TRANSCRIPT_DIR"] = os.path.join(tower_data_path, "transcripts")

    print("Environment variables set for Tower Engine.")

    # 5. Engine Handoff
    print("Handing off control to Tower Engine Orchestrator...")
    
    persistence_evidence = pm.get_audit_report()
    
    handoff_report = {
        "status": "READY",
        "timestamp": time.time(),
        "env": {
            "TOWER_DATA_PATH": tower_data_path,
            "TOWER_SAVE_DIR": os.environ["TOWER_SAVE_DIR"]
        },
        "persistence_evidence": persistence_evidence
    }
    
    handoff_log_path = os.path.join(tower_data_path, "logs", "launcher_handoff.json")
    with open(handoff_log_path, 'w') as f:
        json.dump(handoff_report, f, indent=2)
    
    # Also write a dedicated persistence audit artifact for STAGE-029 validation
    persistence_audit_path = "outputs/audits/kiosk_launcher_persistence_audit.json"
    os.makedirs(os.path.dirname(persistence_audit_path), exist_ok=True)
    with open(persistence_audit_path, 'w') as f:
        json.dump(persistence_evidence, f, indent=2)

    print(f"Handoff report written to {handoff_log_path}")
    print(f"Persistence audit written to {persistence_audit_path}")
    print("--- LAUNCHER COMPLETE, ENGINE RUNNING ---")
    return True

if __name__ == "__main__":
    success = run_kiosk_launcher()
    if not success:
        sys.exit(1)
