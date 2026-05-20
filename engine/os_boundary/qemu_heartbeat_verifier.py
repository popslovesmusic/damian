import json
import re
import os

def verify_boot_signals(log_path, contract_path):
    if not os.path.exists(log_path):
        return {"ok": False, "error": f"Log file not found: {log_path}"}
    
    with open(contract_path, 'r') as f:
        contract = json.load(f)
    
    with open(log_path, 'r') as f:
        log_content = f.read()

    results = {
        "contract_id": contract["contract_id"],
        "signals_detected": [],
        "missing_signals": [],
        "failures_detected": [],
        "verdict": "FAIL"
    }

    for signal in contract["required_signals"]:
        if re.search(signal["pattern"], log_content):
            results["signals_detected"].append(signal["id"])
        else:
            results["missing_signals"].append(signal["id"])

    for failure in contract["failure_signals"]:
        if re.search(failure["pattern"], log_content):
            results["failures_detected"].append(failure["id"])

    if not results["missing_signals"] and not results["failures_detected"]:
        results["verdict"] = "PASS"
    
    return results

if __name__ == "__main__":
    # Example usage (stub)
    log_file = "outputs/audits/qemu_serial_capture.log"
    contract_file = "engine/os_boundary/contracts/qemu_boot_verification_contract.json"
    
    # Create a dummy log for testing the validator if it doesn't exist
    if not os.path.exists(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            f.write("Linux version 6.1.0-debian (gcc 12.2.0)\n")
            f.write("Run /sbin/init as init process\n")
            f.write("Mounting Persistent Tower Data Partition\n")
            f.write("Starting Damian Tower Kiosk Launcher\n")
            f.write("Handing off control to Tower Engine Orchestrator\n")
            f.write("--- ENGINE READY ---\n")

    report = verify_boot_signals(log_file, contract_file)
    print(json.dumps(report, indent=2))
