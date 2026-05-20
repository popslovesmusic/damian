# Console Status Traversal Pressure

This document explains the integration of traversal pressure evidence into the console `status` command within the MVP Text Console.

## Overview

The `status` command has been updated to include a material assessment of the player's spatial vulnerability. It provides a real-time summary of how current material factors (inventory weight, gear condition, environmental mutations) are aggregating into a "Traversal Risk."

## Derived Evidence

When a player checks their status, the console gathers evidence from several subsystems to calculate current traversal hazard:

1.  **Capacity Pressure**: Derived from the current `inventory_state`. The physical burden of held items increases movement friction.
2.  **Mutation Pressure**: Derived from the current floor's `active_mutations`. Environmental instability makes routes more unpredictable.
3.  **Combat Exposure**: Derived from recent combat activity (using `durability_pressure_observed` as a proxy). A high-conflict history implies a higher risk of being intercepted during movement.
4.  **Repair Burden**: Derived from the `aggregate_pressure` of the player's `equipment_loadout`. Gear in poor condition increases the hazard of exploration.

## Strategic Observability

By displaying the **Traversal Risk** in the status message, the "Tower" ensures that spatial decisions are always visible as material tradeoffs. A player with a "HIGH" capacity pressure can see their escape risk increase in real-time, forcing them to decide whether to continue ascending or retreat before the burden becomes insurmountable.

## Payload Integration

The structured `status` payload now includes:

*   **`traversal_pressure_summary`**: A human-readable summary of the movement hazard.
*   **`traversal_pressure`**: The aggregate weighted burden value (0.0 to 1.0).
*   **`escape_risk`**: The calculated risk of failing a retreat or escape.
*   **`traversal_pressure_inputs`**: A breakdown of the contributing material factors (capacity, mutation, combat, and repair pressures).

This ensures that the "journey" is as auditable and reviewable as the "battle" in post-session transcripts and playtest reports.
