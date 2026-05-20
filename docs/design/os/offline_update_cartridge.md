# Offline Update Cartridge and Patch Migration Runtime

## Overview
Stage 038 establishes the infrastructure for secure, offline updates of the Tower OS and its content. This system allows the Tower to evolve while ensuring that every update is verified, non-destructive, and fully auditable.

## Update Boundary
The `engine/os_boundary/contracts/update_cartridge_boundary.json` defines the strict safety rules:
- **Offline Only**: Updates are delivered via physical media, eliminating network dependencies and risks.
- **Hash Verification**: All update cartridges must pass SHA256 integrity checks before processing.
- **Mandatory Backup**: No state can be modified without a full, verified backup of the `TOWER_DATA` partition.
- **Dry-Run Requirement**: Every patch migration must be simulated as a dry-run before real execution.

## Update Manifest Contract
The manifest contract (`engine/os_boundary/contracts/update_cartridge_manifest_contract.json`) specifies the required fields for an update cartridge:
1. **Targeting**: Target version and minimum source version requirements.
2. **Payloads**: Declarations of OS patches, content updates, and migration scripts.
3. **Approval**: An explicit admin approval phrase is required for execution.
4. **Rollback**: Information required to reverse the update if necessary.

## Update Manager
The `engine/os_boundary/update_manager.py` component manages the update lifecycle:
1. **Verification**: Validates the cartridge schema and integrity.
2. **Dry-Run Planning**: Generates a discrete set of migration steps for operator review.
3. **Backup Gating**: Enforces the creation of pre-update recovery points.

## Terminal Integration
The Restricted Admin Terminal includes an `update` command family:
- `update scan <path>`: Verifies an offline cartridge.
- `update plan`: Generates the patch migration dry-run.
- `update audit`: Exposes the history and evidence of update attempts.

## Conclusion
The offline update cartridge system provides a robust and secure path for the Tower's evolution. It ensures that memory, lineage, and recoverability are preserved across every update cycle.
