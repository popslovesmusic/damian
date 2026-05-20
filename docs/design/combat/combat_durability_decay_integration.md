# Combat Durability Decay Integration

This document explains how bounded durability decay is integrated into deterministic combat resolution in the Tower Engine.

## Overview

In the Tower Engine, combat is not just a test of health and damage; it is a **mechanical stress test** for the player's gear. The `combat_resolution_stub` has been updated to materially degrade the condition of equipped items based on the intensity of the encounter and the burden of the player's loadout.

## Integration Logic

The stub uses the following rules to apply material wear during combat:

1.  **Deterioration Path**: When a combat session includes an `equipment_loadout`, the `resolve_combat_session` function calls the `durability_decay_stub`.
2.  **Pressure Scaling**: The amount of durability lost scales with:
    *   **Combat Pressure**: High-stakes encounters drive significantly more wear.
    *   **Capacity Pressure**: Overloaded players place more strain on their gear.
    *   **Repair Pressure**: Higher upkeep items (from their `operational_profile`) are inherently more fragile.
3.  **Audit Recording**: Every item that undergoes decay produces a `DurabilityDecayEvent`. These events are captured in the structured combat result and recorded in transcripts.
4.  **No Permanent Breakage**: Items can reach 0 durability and lose operational effectiveness, but they are not deleted from the inventory during the MVP phase.

## Boundedness and Safety

*   **Pipeline Preservation**: Durability decay is a consequence of combat, but it does not bypass the `mvp_outcome_pipeline`. The final decision on victory, defeat, or mutation remains with the pipeline.
*   **Consequence Integrity**: Gear condition is a material stratégico factor. A player with 0 durability gear remains in a high-risk state, potentially biasing future encounters toward defeat until the `repair` command is used.
*   **Identity Preservation**: The system ensures that item IDs and names remain consistent even as their condition changes.

## Observed Evidence

The structured combat result now includes:
*   `durability_decay_applied`: Confirms gear wear occurred.
*   `durability_events`: A list of detailed decay records for every equipped item.
*   `updated_equipment_loadout`: The new state of the player's gear after the encounter.
*   `durability_pressure_observed`: True if material wear was a significant factor in the session.

This integration ensures that "Equipment Pressure" is no longer just a reported number, but a material drain on the player's long-term sustainability.
