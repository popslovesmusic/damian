# Minimal Durability Decay Stub

This document explains the deterministic durability decay stub implementation for the Tower Engine MVP.

## Overview

The `durability_decay_stub` provides a way to materially degrade equipment based on operational usage and environmental strain. It bridges the gap between "Equipment Pressure" and "Material strategic burden" by turning combat and maintenance costs into actual durability loss.

## Calculation Rules

To ensure game balance and maintain the MVP scope, the following rules are enforced:

1.  **Deterministic Formula**: Durability loss is calculated based on fixed weights applied to `combat_pressure`, `repair_pressure`, `mutation_affinity`, and `capacity_pressure`.
2.  **Bounded Decay**:
    *   Durability cannot drop below `0`.
    *   If current durability is `0`, no further decay events will apply loss to that item.
3.  **Preserved Identity**: The stub always operates on copies and ensures that core fields like `equipment_item_id` and `item_name` remain unchanged.
4.  **Material Demand**: By degrading gear, the stub creates a material strategic demand for the `repair` command and associated materials (established in Stage 008).

## Non-Repair Scope

This stub is strictly responsible for **deterioration**. It does not handle:
*   Restoring durability (Repair runtime is a separate future stage).
*   Automatic item deletion (Gear remains in inventory at 0 durability).
*   Stat penalties (While durability reflects condition, for the MVP it does not yet mechanically scale damage/defense).

## Integration Flow

1.  **Combat Resolution**: An encounter result provides a `combat_pressure` value.
2.  **Loadout Decay**: The `apply_loadout_durability_decay` function iterates through all equipped items.
3.  **Event Recording**: Every decayed item produces a `DurabilityDecayEvent` record.
4.  **Transcript Visibility**: These events are captured in console transcripts, making equipment wear observable for auditing.
