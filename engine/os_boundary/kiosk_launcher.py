import os
import json
import sys
import subprocess
import time
from engine.os_boundary.persistence_manager import PersistenceManager
from engine.os_boundary.launcher_hardener import KioskLauncherHardener
from engine.os_boundary.cartridge_verifier import CartridgeVerifier
from engine.os_boundary.lineage_manager import LineageManager

def run_kiosk_launcher():
    print("--- DAMIAN TOWER KIOSK LAUNCHER STARTING ---")
    
    # 1. Initialize Hardener and Persistence
    os_root = os.environ.get("TOWER_OS_ROOT", "/")
    data_root = os.environ.get("TOWER_DATA_PATH", "/tower/data")
    hardener = KioskLauncherHardener(os_root, data_root)
    
    # 2. Environment Verification
    if not hardener.verify_environment():
        print("ERROR: Environment verification failed.")
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_environment_verification.json")
        return False
    print(f"Verified TOWER_OS at {os_root} and TOWER_DATA at {data_root}")

    # 3. Artifact Lineage and Version Scanning
    print("Scanning artifact lineage and data versions...")
    with open("engine/os_boundary/contracts/artifact_lineage_boundary.json", 'r') as f:
        boundary_c = json.load(f)
    with open("engine/os_boundary/contracts/lineage_manifest_contract.json", 'r') as f:
        lineage_c = json.load(f)
    with open("engine/os_boundary/contracts/persistent_data_version_contract.json", 'r') as f:
        version_c = json.load(f)

    lm = LineageManager(data_root, boundary_c, lineage_c)
    detected_version = lm.scan_data_version(version_c)
    
    lineage_manifest = lm.generate_artifact_manifest("tower-damian-v1", "tower_os_image", "1.0.0", "0.0.1")
    lineage_evidence = lm.get_final_evidence()

    if lineage_evidence["compatibility"] == "INCOMPATIBLE":
        print(f"ERROR: Incompatible persistent data version detected: {detected_version}")
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_lineage_result.json")
        return False

    # 4. Persistence Path Guard & Initialization
    persistence_paths = ["saves", "logs", "transcripts", "mods", "content_packs", "crash_reports", "state_snapshots", "artifacts"]
    if not hardener.enforce_persistence_guard(persistence_paths):
        print("ERROR: Persistence path guard violation detected.")
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_persistence_guard.json")
        return False
    
    # 5. Content Pack Cartridge Verification
    print("Verifying content pack cartridges...")
    verifier = CartridgeVerifier(
        "engine/os_boundary/contracts/content_pack_cartridge_boundary.json",
        "engine/os_boundary/contracts/content_pack_manifest_contract.json"
    )
    
    # Check default pack (Damian)
    damian_dir = os.path.join(os_root, "usr/share/damian/content/damian")
    if not os.path.exists(damian_dir):
        damian_dir = "content/damian"
    
    damian_manifest_path = os.path.join(damian_dir, "cartridge_manifest.json")
    cartridge_verdict = "FAIL"
    
    if os.path.exists(damian_manifest_path):
        with open(damian_manifest_path, 'r') as f:
            manifest = json.load(f)
        
        if verifier.verify_manifest_schema(manifest) and \
           verifier.safety_scan(manifest) and \
           verifier.verify_hashes(damian_dir, manifest):
            cartridge_verdict = "PASS"
            print(f"Content pack 'damian' verified.")
        else:
            print(f"ERROR: Content pack 'damian' verification failed.")
    else:
        print("ERROR: Default content pack manifest missing.")

    if cartridge_verdict != "PASS":
        hardener.emit_failure_audit("outputs/audits/kiosk_launcher_cartridge_verification_result.json")
        return False

    # 6. Explicit Runtime Config Handoff
    runtime_config = hardener.generate_runtime_config()
    
    # 7. Setup Environment Variables for Engine
    os.environ["TOWER_SAVE_DIR"] = runtime_config["save_root"]
    os.environ["TOWER_LOG_DIR"] = runtime_config["log_root"]
    os.environ["TOWER_ARTIFACT_DIR"] = runtime_config["artifact_root"]

    # 8. Engine Handoff
    print("Handing off control to Tower Engine Orchestrator...")
    
    cartridge_evidence = verifier.get_final_evidence()
    
    handoff_report = {
        "status": "READY",
        "timestamp": time.time(),
        "runtime_config": runtime_config,
        "hardening_verdict": "PASS",
        "cartridge_verdict": cartridge_verdict,
        "cartridge_evidence": cartridge_evidence,
        "lineage_evidence": lineage_evidence,
        "artifact_manifest": lineage_manifest
    }
    
    handoff_log_path = os.path.join(runtime_config["log_root"], "launcher_handoff.json")
    with open(handoff_log_path, 'w') as f:
        json.dump(handoff_report, f, indent=2)
    
    # Emit lineage audit artifact
    with open("outputs/audits/kiosk_launcher_lineage_result.json", 'w') as f:
        json.dump(lineage_evidence, f, indent=2)

    print(f"Handoff report written to {handoff_log_path}")
    print("--- LAUNCHER COMPLETE, ENGINE RUNNING ---")
    return True

if __name__ == "__main__":
    success = run_kiosk_launcher()
    if not success:
        sys.exit(1)
