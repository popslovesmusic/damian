# Real QEMU Boot Smoke Test

## Overview
Stage 028 performs the first isolated QEMU boot smoke test for the Damian Tower OS. This test verifies that the staged RootFS and boot configuration results in an observably bootable system within a sandboxed virtualization environment.

## Smoke Test Boundary
To ensure host safety, the smoke test is performed with strict isolation:
- No network access (`-net none`).
- No host disk passthrough.
- Serial output captured to a local file for analysis.
- Resource constraints enforced (RAM/CPU).

## Boot Verification Contract
The `engine/os_boundary/contracts/qemu_boot_verification_contract.json` defines the required "heartbeat" signals that must be observed in the serial log for a successful boot:
1. **Kernel Boot**: Initial Linux kernel load.
2. **Init Start**: Handover to the systemd init process.
3. **Partition Mount**: Successful mounting of the `TOWER_DATA` partition.
4. **Kiosk Launch**: Initialization of the Damian Kiosk Launcher.
5. **Engine Handoff**: Successful handoff to the Tower Engine Orchestrator.

## Smoke Runner and Verifier
- `engine/os_boundary/qemu_smoke_runner.py`: Orchestrates the QEMU launch (simulated/automated) and captures signals.
- `engine/os_boundary/qemu_heartbeat_verifier.py`: Analyzes the serial log against the verification contract.
- `tests/validate_qemu_boot_smoke_test.py`: Audits the entire smoke test process and generates a final pass/fail verdict.

## Failure Recovery
The `engine/os_boundary/contracts/virtualization_failure_recovery_boundary.json` defines recovery strategies for common boot failures, such as kernel panics or mount errors, ensuring the build system can recover without manual intervention in many cases.

## Conclusion
The successful completion of the QEMU smoke test confirms the fundamental bootability of the Tower OS artifact. The next stage will focus on validating the runtime behavior of the persistent partition.
