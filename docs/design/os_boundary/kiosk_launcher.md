# Kiosk Runtime Launcher Prototype

## Overview
Stage 023 implements the Kiosk Runtime Launcher, the primary entry point for the Damian Live OS. It is responsible for bridging the gap between the bootloader/OS and the Tower Engine Orchestrator.

## Launcher Responsibilities
The `engine/os_boundary/kiosk_launcher.py` script performs the following critical tasks during boot:
1. **Environment Verification**: Ensures the persistent data partition (`TOWER_DATA`) is correctly mounted and accessible.
2. **Runtime Preparation**: Creates required directory hierarchies within the persistent partition (saves, logs, transcripts) if they are missing.
3. **Engine Configuration**: Maps engine-specific environment variables (`TOWER_SAVE_DIR`, `TOWER_LOG_DIR`, etc.) to the verified persistent partition paths.
4. **Handoff Execution**: Prepares a handoff report (`launcher_handoff.json`) confirming the environment is ready for the Tower Engine Orchestrator.

## Kiosk Boundary Compliance
- The launcher operates within the restricted OS environment.
- It enforces the separation between the immutable OS partition and the mutable data partition.
- It provides a single, controlled path for engine execution.

## Validation
The `tests/validate_kiosk_launcher.py` script verifies the launcher's behavior by:
- Simulating a fresh boot environment.
- Confirming automatic folder creation.
- Validating the handoff report generation.

## Conclusion
With the launcher prototype complete, the Damian Live OS has a reliable entry point that ensures all engine state is correctly directed to the persistent Tower partition.
