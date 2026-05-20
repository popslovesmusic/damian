# Tower OS Recovery and Safe Repair Runtime

## Overview
Stage 037 implements the recovery and safe repair infrastructure for the Tower OS. This system ensures that while the OS core remains immutable, the persistent data layer (`TOWER_DATA`) can be scanned for corruption, isolated when damaged, and repaired using validated snapshots—all through bounded and auditable procedures.

## Recovery Boundary
The `engine/os_boundary/contracts/recovery_runtime_boundary.json` establishes strict safety constraints:
- **Core Protection**: Recovery actions are prohibited from mutating the `TOWER_OS` partition.
- **Isolation Priority**: Corrupted state is moved to an isolated namespace rather than being deleted, preserving evidence for diagnostics.
- **Operator Gating**: Destructive repairs require explicit confirmation from the operator.
- **Auditable History**: Every recovery attempt generates a structured audit log that is preserved as part of the artifact lineage.

## Recovery Manager
The `engine/os_boundary/recovery_manager.py` component orchestrates the repair lifecycle:
1. **Integrity Scanning**: Scans required domains (saves, logs, content packs) for missing, unreadable, or inconsistent data.
2. **Runtime Isolation**: Safely renames corrupted directories to prevent further engine interference while preserving the data for review.
3. **Simulation Mode**: Allows for full dry-runs of snapshot restoration to verify plan validity without risk of data loss.
4. **Structure Repair**: Restores missing required directory hierarchies within the persistent partition.

## Terminal Integration
The Restricted Admin Terminal has been expanded with a `recovery` command family:
- `recovery scan`: Performs a real-time integrity check of the persistence layer.
- `recovery simulate <id>`: Executes a dry-run of a specific recovery plan.
- `recovery audit`: Exposes the detailed evidence and history of recovery actions.

## Conclusion
The recovery and safe repair runtime ensures that Damian remains a resilient platform. It fulfills the core identity rule that the Tower's history and memory must be preserved and traceable, even in the event of failure or degradation.
