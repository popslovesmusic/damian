# Physical USB Flashing Handoff and Safety Gate

## Overview
Stage 034 establishes the final guarded layer between validated Tower OS image artifacts and physical media. This phase focuses on "anti-host-destruction" safety gates, ensuring that the process of creating bootable USB devices is explicit, operator-verified, and strictly isolated from host system disks.

## Safety Boundaries
The `engine/os_boundary/contracts/usb_handoff_boundary.json` defines non-negotiable safety rules:
- **No Auto-Flashing**: Automated scripts are prohibited from performing direct physical writes.
- **Internal Disk Protection**: NVMe and SATA devices identified as internal are automatically rejected to prevent host OS destruction.
- **Read-Only Detection**: All device enumeration is performed in a read-only mode to prevent accidental metadata corruption.
- **Hash Mandatory**: No image can be planned for flashing without a verified SHA256 integrity check.

## Handoff Components
1. **Flash Handoff Manager**: `engine/os_boundary/flash_handoff_manager.py` orchestrates the safety-check lifecycle.
2. **Device Enumeration**: Filters available block devices to allow only removable USB media.
3. **Dry-Run Planning**: Generates a discrete set of actions (unmount, write, verify) for operator review without executing them.
4. **Operator Acknowledgment Gate**: Requires the operator to type an explicit confirmation phrase (e.g., `FLASH_TOWER_ARTIFACT_TO_sdb`) to acknowledge destructive risk.

## Admin Terminal Integration
Admins can monitor the status of flashing handoffs through the `flash status` command in the Restricted Admin Terminal. This provides a clear audit trail of which devices were detected, which were rejected, and whether the acknowledgment gate was passed.

## Conclusion
The physical USB flashing handoff ensures that Damian artifacts can be safely delivered to hardware while maintaining the highest level of protection for the developer's host environment.
