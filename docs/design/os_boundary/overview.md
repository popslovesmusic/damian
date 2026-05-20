# Game Cartridge OS Boundary

## Overview
Damian operates as a bootable live/kiosk Linux game environment where the OS itself becomes part of the Tower artifact. Booting the system should feel like entering the Tower. Persistence is controlled, explicit, and confined to specific partitions.

## Immutability vs Persistence
The OS is divided into two strict partitions:
1. **TOWER_OS**: A read-only, immutable live system containing the Linux base, game runtime, engine binaries, and verified content packs.
2. **TOWER_DATA**: A read-write, persistent partition containing player saves, state, logs, mods, and configuration overrides.

## Kiosk Mode
- The system boots directly into the Damian Game Launcher.
- OS boot messages are hidden to maintain immersion.
- The launcher strictly separates the user from the underlying desktop environment.
- Modifying the bootloader or customizing the kernel is strictly prohibited at this stage.

## Admin Terminal
- Terminal access is heavily restricted.
- No remote administration (SSH) is permitted at this stage.
- Destructive disk partitioning actions are blocked.

## Content Packs
- Content packs are fully verifiable.
- Default content packs reside in the immutable `TOWER_OS`.
- Overrides and mods reside in `TOWER_DATA`.

## Deployment Artifact
- The current target artifact is a Live USB image based on Debian stable minimal or Ubuntu Server minimal.
- ISO build automation and driver bundle creation are out of scope for the current boundary.

## Security & Recovery
- No network-based runtime updates.
- No real multiplayer servers.
- Recovery is performed by flashing a new Live USB image.
