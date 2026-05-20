# Minimal Equipment Pressure Stub

This document explains the deterministic equipment pressure stub implementation for the Tower Engine MVP.

## Overview

The `equipment_pressure_stub` provides a way to calculate the aggregate operational burden placed on a player by their current equipment loadout. This ensures that gear is not just a source of power, but a source of strategic tradeoff and upkeep cost.

## Calculation Rules

To ensure game balance and maintain the MVP scope, the following rules are enforced:

1.  **Averaging Logic**: Aggregate pressure values (repair, visibility, affinity, capacity, risk) are calculated as the arithmetic average of the `operational_profile` values of all equipped items.
2.  **Safety Bound Verification**: The `bounded_rules_clean` flag is set to `True` only if **none** of the equipped items have any active bypass flags (e.g., `grants_invulnerability`).
3.  **Deterministic & Predictable**: For any given list of item records, the aggregate pressure is always the same, allowing for reliable audit transcripts.
4.  **Pressure Range**: All individual and aggregate pressure values are strictly bounded between `0.0` and `1.0`.

## Aggregate Pressure Profile

The stub produces an aggregate profile with the following axes:

*   **Repair Pressure**: The estimated upkeep cost multiplier.
*   **Residue Visibility**: The base visibility for residue generation.
*   **Mutation Affinity**: The sensitivity to floor and replay mutations.
*   **Capacity Pressure**: The physical burden and flexibility penalty.
*   **Risk Profile**: The inherent volatility of the equipment's performance.

## Integration Flow

1.  **Loadout Definition**: A list of `EquipmentItem` records is provided.
2.  **Aggregate Calculation**: The stub calculates the averages and verifies safety flags.
3.  **Loadout Building**: A complete `EquipmentLoadout` object is constructed, including a unique ID and player reference.
4.  **Validation**: The loadout is validated against the schema.
5.  **Combat Integration**: The aggregate pressure is used by the combat resolution stub to bias outcomes (implemented in the next patch).
