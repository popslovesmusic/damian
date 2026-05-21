# Content Pipeline, Biomes, and Procedural Tower Expansion

## Overview
Stage 062 establishes the infrastructure for the Tower's procedural expansion into diverse ecological regions. In Damian, biomes are not just visual changes; they are "Procedural Wounds" in the Tower that introduce unique environmental pressures, hazard ecologies, and landmark distributions while maintaining a coherent systemic identity.

## Biome Boundary
The `engine/content/biomes/contracts/biome_boundary.json` defines the strict safety rules:
- **Tower Identity**: Every biome must preserve the foundational hostility and atmospheric tone of the Tower.
- **No Disconnected Zones**: Biomes are integrated regions of the Tower, not isolated "theme-park" levels.
- **Readable Hazards**: Environmental hazards (e.g., `PRESSURE_FOG`) must remain recognizable and auditable to ensure fair survival gameplay.
- **Author Scalability**: The pipeline supports expansion through the Author SDK, allowing for community-driven biome modules within bounded parameters.

## Biome Content Contract
The biome contract (`engine/content/biomes/contracts/biome_contract.json`) specifies the required state for a region profile:
1. **Pressure Profile**: Defines the baseline environmental instability and detection risk for the biome.
2. **Hazard Ecology**: Tracks the primary procedural hazards (e.g., `COLLAPSE_RISK`) and their density.
3. **Landmark & Relay Placement**: Ensures navigation clarity through recognizable spires and scattered relay nodes.
4. **Enemy Pressure**: Adapts the local predator and scavenger ecologies to match the biome's identity.

## Biome Manager
The `engine/content/biomes/runtime/biome_manager.py` component manages the expansion lifecycle:
1. **Profile Generation**: Produces hash-verified biome manifests based on type and systemic pressure.
2. **Identity Validation**: Gathers evidence that the generated region preserves mandatory landmarks and atmospheric consistency.
3. **Expansion Smoke Testing**: Simulates procedural transitions into new biomes to ensure readability and recoverability are maintained under load.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `biome status` and `biome audit` commands to monitor active region configurations and review the history of procedural expansion.
- **Dashboard**: The player dashboard provides lore-compatible view of "Regional Identity" and the current "Environmental Profile" of their location.

## Conclusion
The Procedural Biome system ensures that Damian can scale massively without losing its core identity. It provides a robust and auditable framework for world expansion, fostering a sense of discovery that is as dangerous and consequential as the Tower itself.
