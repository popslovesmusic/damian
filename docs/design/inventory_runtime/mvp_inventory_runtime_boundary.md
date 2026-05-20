# MVP Inventory Runtime Boundary

This document defines the foundational framework for the material inventory runtime in the Tower Engine.

## Philosophy: Abstract Pressure to Material Burden

In previous stages, economic costs (gold, materials, upkeep) were "reported" or "observed" in transcripts but did not mechanically affect the player's state. The **Inventory Runtime** exists to bridge this gap, ensuring that every resource sink and loot reward has a material consequence:

1.  **Finite Capacity**: Supplies and gear take up space. High capacity pressure reduces operational flexibility and biases the player toward retreat.
2.  **Explicit Deduction**: Consumables (potions) and repair materials are mechanically removed from the inventory. If the player lacks the necessary resources, maintenance fails, and pressure increases.
3.  **Auditability**: Every change to the inventory state is recorded as an `InventoryTransaction`, providing a permanent audit trail for wealth and resource flow.

## Runtime Responsibilities

*   **Tracking**: Maintain accurate counts of items (potions, fragments) and currencies (gold, shards).
*   **Capacity Enforcing**: Accumulate capacity pressure from all held items and reject transactions that would exceed the hard MVP limit.
*   **Transaction Guarding**: Ensure that deductions do not create negative quantities and that failed operations do not corrupt the inventory state.
*   **Safety Preservation**: Verify that incoming loot or transactions do not violate the core anti-inflationary rules (e.g., no invulnerability flags).

## Identity Rules (Consequence Preservation)

To maintain engine integrity, the inventory system follows these strict rules:

*   **No Defeat Cancellation**: Having a full inventory or specific items cannot bypass the consequences of `DEFEAT_DROP`.
*   **No Residue Bypass**: Inventory items cannot prevent the generation of residue from player actions.
*   **No Infinite Storage**: Capacity is a hard strategic constraint; it cannot be bypassed or scaled infinitely.
*   **Visibility**: Resource pressure must remain visible to the player and the engine's auditing tools.

## Non-Goals (Scope Containment)

To prevent scope creep, the following are explicitly **NOT** part of the MVP Inventory Runtime:
*   **Full Equipment Effects**: Real-time gear stat scaling.
*   **Shops/Market**: Direct player-to-NPC or player-to-player trading.
*   **Inventory UI**: Visual representation of the bag (remains console/data-driven).
*   **Crafting**: Combining items to create new ones.
