# Virtualization Boot Strategy

## Overview
Stage 026 defines the strategy for validating the Damian Tower OS image using virtualization (QEMU). This allows us to test the entire boot cycle—from kernel load to kiosk launcher start—without requiring physical hardware or risky host modifications.

## Isolation and Safety
To maintain the safety of the development host, the following virtualization boundaries are enforced:
1. **Network Isolation**: The VM is configured with `-net none` or restricted user-mode networking. It cannot access the local network or the internet unless explicitly enabled for specific tests.
2. **Storage Isolation**: Only the generated image file is attached as a virtual drive. No host directories are shared via VirtFS or similar mechanisms.
3. **No Root Privilege**: QEMU is launched as a standard user process.

## Boot Success Criteria
We verify the success of a boot by monitoring the virtual serial port. The engine looks for the following "heartbeat" messages:
- `[TOWER_OS] Kernel Init Complete`: Confirms the Linux kernel has loaded correctly from the read-only partition.
- `[TOWER_OS] Mounting TOWER_DATA`: Confirms the persistent partition has been identified and mounted.
- `[TOWER_OS] Starting Damian Kiosk Launcher`: Confirms the kiosk service is operational and handing off to the Tower Engine.

## Automated Validation
The `tests/validate_qemu_boot_parameters.py` script audits the proposed QEMU command line to ensure it adheres to the safety and resource constraints defined in the boundary contract.

## Conclusion
Virtualization provides a high-fidelity, low-risk environment for verifying the OS boundary and boot integrity of the Tower artifact.
