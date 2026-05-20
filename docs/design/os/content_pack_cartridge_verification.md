# Content Pack Cartridge Verification

## Overview
Stage 032 introduces a "cartridge" model for content packs in the Tower OS. This ensures that all game content—worlds, story modules, and assets—are verifiable, sandboxed, and cannot compromise the OS core or the player's host system.

## Verification Boundary
The `engine/os_boundary/contracts/content_pack_cartridge_boundary.json` defines the safety rules:
- **Immutability**: Content packs are read-only and cannot mutate the `TOWER_OS` partition.
- **Verification Mandatory**: No content can be loaded without passing manifest audit, safety scan, and hash verification.
- **Isolation**: Content packs are restricted to declared asset directories and cannot execute arbitrary shell scripts or binaries.

## Cartridge Manifest
Each content pack must include a `cartridge_manifest.json` (governed by `engine/os_boundary/contracts/content_pack_manifest_contract.json`). This manifest includes:
1. **Metadata**: ID, version, engine compatibility, and pack type.
2. **File Declaration**: A list of all files belonging to the cartridge.
3. **Integrity Manifest**: SHA256 hashes for every declared file.
4. **Safety Flags**: Explicitly bounded flags declaring the immutable nature of the pack.

## Security Layers
1. **Hash Verification**: `CartridgeVerifier` compares on-disk files against the manifest hashes to detect tampering or corruption.
2. **Safety Scan**: Rejects any cartridge containing unsafe paths (traversal) or executable payloads (scripts/binaries).
3. **Manifest Audit**: Ensures no forbidden fields (like `shell_command` or `device_access`) are present.

## Integration
- **Kiosk Launcher**: The launcher now verifies the default `damian` content pack before handing off control to the Tower Engine. If verification fails, the boot process is halted with a clear audit.
- **Restricted Terminal**: Admins can use the `content status` command to inspect the verification evidence of loaded cartridges.

## Conclusion
The cartridge model ensures that Damian remains a secure and stable platform, where content can be expanded or modified without risking the integrity of the underlying Tower OS.
