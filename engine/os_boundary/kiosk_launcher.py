import os
import json
import sys
import subprocess
import time
from engine.os_boundary.persistence_manager import PersistenceManager
from engine.os_boundary.launcher_hardener import KioskLauncherHardener
from engine.os_boundary.cartridge_verifier import CartridgeVerifier

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
    
    # 4. Content Pack Cartridge Verification
    print("Verifying content pack cartridges...")
    verifier = CartridgeVerifier(
        "engine/os_boundary/contracts/content_pack_cartridge_boundary.json",
        "engine/os_boundary/contracts/content_pack_manifest_contract.json"
    )
    
    # Check default pack (Damian)
    damian_dir = os.path.join(os_root, "usr/share/damian/content/damian")
    # For prototype support, if os_root is build/live_os/rootfs_staging, it's correct
    if not os.path.exists(damian_dir):
        # Fallback for dev environment
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

    # 5. Explicit Runtime Config Handoff
    runtime_config = hardener.generate_runtime_config()
    
    # 6. Setup Environment Variables for Engine (Mapping from hardener's config)
    os.environ["TOWER_SAVE_DIR"] = runtime_config["save_root"]
    os.environ["TOWER_LOG_DIR"] = runtime_config["log_root"]
    os.environ["TOWER_ARTIFACT_DIR"] = runtime_config["artifact_root"]

    print("Explicit runtime configuration generated and environment variables set.")

    # 7. Engine Handoff
    print("Handing off control to Tower Engine Orchestrator...")
    
    cartridge_evidence = verifier.get_final_evidence()
    
    handoff_report = {
        "status": "READY",
        "timestamp": time.time(),
        "runtime_config": runtime_config,
        "hardening_verdict": "PASS",
        "cartridge_verdict": cartridge_verdict,
        "cartridge_evidence": cartridge_evidence
    }
    
    handoff_log_path = os.path.join(runtime_config["log_root"], "launcher_handoff.json")
    with open(handoff_log_path, 'w') as f:
        json.dump(handoff_report, f, indent=2)
    
    hardener.emit_success_audit("outputs/audits/kiosk_launcher_environment_verification.json")
    # Also emit specific cartridge verification result for STAGE-032 audit
    with open("outputs/audits/kiosk_launcher_cartridge_verification_result.json", 'w') as f:
        json.dump(cartridge_evidence, f, indent=2)

    print(f"Handoff report written to {handoff_log_path}")
    print("--- LAUNCHER COMPLETE, ENGINE RUNNING ---")
    return True

if __name__ == "__main__":
    success = run_kiosk_launcher()
    if not success:
        sys.exit(1)
