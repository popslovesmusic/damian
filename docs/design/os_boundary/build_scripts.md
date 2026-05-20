# Prototype Live USB Build Scripts

## Overview
Stage 022 establishes a non-destructive build environment for the Damian Live/Kiosk OS. It provides the mechanisms to plan and validate the assembly of a bootable image without performing any destructive operations on the host system.

## Build Configuration
The build is governed by `os/kiosk/build_config.json`, which defines:
- Target OS base (Debian/Ubuntu)
- Partition layout (TOWER_OS, TOWER_DATA)
- Kiosk user settings
- Staging and output paths

## RootFS Manifest
The `os/kiosk/rootfs_manifest.json` defines the structure of the immutable OS partition, including:
- Directory hierarchies
- File placements (Launcher scripts, systemd units)
- Symlinks for persistence mapping

## Systemd Templates
- `tower-kiosk.service`: Manages the auto-launch of the Damian game environment.
- `tower-data.mount`: Manages the mounting of the persistent data partition.

## Non-Destructive Build Plan
The `engine/os_boundary/build_plan_generator.py` script translates the configuration and manifest into a discrete set of build steps (`build/live_os/build_plan.json`). This plan is generated without executing any file operations outside the build root.

## Dry-Run Validation
The `tests/validate_live_usb_build_scripts.py` validator ensures that:
- No destructive disk commands (format, partition) are present in the plan.
- All file operations are confined to the project's build boundaries.
- All required templates are present.

## Conclusion
This stage provides the scaffolding for image creation while maintaining strict safety boundaries. The next stage will focus on the Kiosk Runtime Launcher prototype.
