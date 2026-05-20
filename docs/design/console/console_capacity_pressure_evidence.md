# Console Capacity Pressure Evidence

This document explains the visibility and strategic significance of inventory capacity pressure in the MVP Text Console.

## Overview

Inventory Capacity Pressure is a material metric that represents the estratégico burden of held items. By making this pressure visible in console commands, the system ensures that the player is always aware of their remaining estratégico flexibility and the consequences of their supply management choices.

## Visibility in Commands

Capacity pressure evidence is integrated into the following console commands:

### `status`
Displays the current strategic band (e.g., LOW, MODERATE) in the status message and provides the full structured `capacity_pressure_summary` in the payload. This allows for continuous monitoring of bag space without executing a transaction.

### `combat`
Following a successful combat encounter, the `combat` command applies the resulting loot to the inventory. The response payload includes the updated capacity pressure, allowing auditors to see how much strategic space the new rewards occupied.

### `potion` and `repair`
These material drain commands mechanically reduce the used capacity of the inventory. Successful executions report the lowered pressure (increased flexibility), while failed attempts (due to insufficient supplies) report the pre-transaction pressure to highlight the strategically locked state.

## Strategic Bands

To ensure the burden is easily reviewable, the console uses the following strategic bands:

*   **EMPTY**: Total flexibility; no items held.
*   **LOW**: Negligible burden.
*   **MODERATE**: Strategic tradeoffs starting to matter.
*   **HIGH**: Heavy burden; flexibility severely reduced.
*   **FULL**: Bag is full; no additional material rewards can be added.
*   **INVALID**: Over-capacity or corrupted state (fails safely).

## Boundedness Rules

*   **Material Accumulation**: Capacity pressure is a direct ratio of weight to space (`used_capacity / inventory_capacity`).
*   **Linear Scaling**: The pressure metric scales linearly from `0.0` to `1.0`.
*   **Auditability**: Every material command provides the current pressure and band, ensuring a consistent evidence trail in transcripts.

## Strategic Impact

By exposing capacity pressure in the console, the "Tower" forces the player into material strategic dilemmas. A player operating in the **HIGH** band must decide whether to consume potions early (freeing space but risking future health) or abandon potential loot (preserving space but slowing progression).
