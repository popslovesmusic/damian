# Tower OS Artifact Lineage and Version Migration

## Overview
Stage 033 establishes the mechanisms for tracking the lineage of Tower OS artifacts and ensuring safe version migrations for persistent data. This ensures that as the Tower evolves, its memory (saves, state, configuration) is preserved or migrated through explicit, auditable paths.

## Artifact Lineage
The `engine/os_boundary/lineage_manager.py` component tracks the provenance of Tower artifacts, including:
- **Image and RootFS Hashes**: Ensures the integrity of the base OS.
- **Content Pack Versions**: Tracks which world versions are active.
- **Source Provenance**: Records the source commit and build timestamp.
- **Migration Status**: Tracks whether the current state has undergone version upgrades.

## Version Migration
Persistent data (saves and state) is governed by a version contract (`engine/os_boundary/contracts/persistent_data_version_contract.json`).
1. **Version Scanning**: During boot, the Kiosk Launcher scans the `TOWER_DATA` partition to detect the current data version.
2. **Compatibility Check**: Compares the detected version against the engine's requirements.
3. **Migration Planning**: If a version mismatch is detected, the `MigrationPlanner` generates a dry-run migration plan. This plan defines the necessary backups and schema transformations without modifying the actual saves.

## Safety and Recovery
- **Backup Mandatory**: Migration modes (other than DRY_RUN) require a full backup of the data partition.
- **Fail-Safe Handoff**: If the launcher detects an incompatible data version without a valid migration path, it halts the boot process to prevent state corruption.
- **Auditable Lineage**: Every boot sequence records lineage evidence, visible through the `lineage status` command in the Restricted Admin Terminal.

## Conclusion
The artifact lineage and migration system ensures that Damian provides a stable and recoverable environment across updates, fulfilling the core rule that the Tower's memory must survive its evolution.
