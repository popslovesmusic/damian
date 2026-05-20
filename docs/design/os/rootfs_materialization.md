# Real RootFS Materialization Boundary

## Overview
Stage 027 transitions the Damian Tower OS build process from image stubs to a real staged RootFS artifact. This materialization happens exclusively within the project's build directory to ensure host safety and isolation.

## Materialization Process
1. **Package Manifest**: `os/kiosk/rootfs_package_manifest.json` defines the engine components and content that must be included in the RootFS.
2. **Materialization Plan**: `engine/os_boundary/rootfs_materialization_planner.py` generates a discrete set of steps to assemble the RootFS.
3. **Staging Stub**: `engine/os_boundary/rootfs_materialization_stub.py` executes the plan, creating the directory hierarchy and staging files into `build/live_os/rootfs_staging/`.

## Safety and Integrity
- **Host Isolation**: All materialization steps are confined to the `build/` directory. No root privileges or host system modifications are required.
- **Integrity Validation**: `tests/validate_rootfs_integrity.py` verifies the staged RootFS against the boundary contract, checking for required subdirectories and ensuring no host binary leaks.
- **Reproducibility**: The staged RootFS is hashed to ensure consistent builds and verifiable artifacts.

## Conclusion
This stage provides a high-fidelity staged RootFS that can be used for squashfs creation and subsequent boot testing, while maintaining a strict non-destructive boundary on the development host.
