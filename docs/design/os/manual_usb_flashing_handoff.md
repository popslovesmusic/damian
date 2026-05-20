# Manual USB Flashing Handoff

## Overview
Stage 025 produces a local bootable image artifact. To ensure the safety of the host system, the Tower Engine automated scripts **never** perform direct writes to physical USB devices or disks. 

This document defines the manual handoff process for flashing the Damian Tower OS image to a USB device for real-world hardware testing.

## Boundary Rules
1. **Host Isolation**: Automated build scripts are confined to the `build/` and `outputs/` directories.
2. **No Root/Sudo Execution**: Build scripts must be runnable as a standard user. Any operation requiring elevation (like `dd` or `fdisk` on a physical device) must be performed manually by the operator.
3. **Explicit Verification**: The operator must verify the SHA256 hash of the image artifact against the generated manifest before flashing.

## Manual Flashing Procedure

### 1. Identify the Target Device
Use a tool like `lsblk` (Linux) or Disk Management (Windows) to identify the correct USB device path (e.g., `/dev/sdX`).

### 2. Verify the Image Hash
Compare the hash of the image artifact with the hash in `build/live_os/images/tower_image_manifest.json`.

```bash
sha256sum build/live_os/images/tower-damian-proto.img
cat build/live_os/images/tower_image_manifest.json | grep hash
```

### 3. Flash the Image
Use a safe flashing tool (like BalenaEtcher or Raspberry Pi Imager) or the command line:

**WARNING: Using `dd` is dangerous. Ensure the `of=` path is correct.**

```bash
sudo dd if=build/live_os/images/tower-damian-proto.img of=/dev/sdX bs=4M status=progress conv=fsync
```

## Post-Flash Verification
1. Ensure the device has two partitions labeled `TOWER_OS` and `TOWER_DATA`.
2. Attempt a test boot on non-production hardware or within a virtual machine (QEMU).

## Conclusion
By keeping the flashing process manual and explicit, we prevent accidental data loss on the developer's host machine while still allowing for physical artifact creation.
