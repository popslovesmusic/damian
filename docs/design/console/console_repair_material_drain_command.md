# Console Repair Material Drain Command

This document explains the implementation of the `repair` command in the MVP Text Console, which enables the material deduction of repair materials from the player's inventory.

## Overview

The `repair` command continues the transition from abstract reported pressure to material strategic burden. While Stage 007 defined the "Equipement Pressure," this command turns the "Repair Pressure" into an actual resource cost that the player must manage.

## Command Behavior

*   **`repair`**: Deducts exactly one `repair_material_basic` from the current inventory.
*   **`repair <quantity>`**: Deducts the specified integer quantity of repair materials.

### Strategic Integration

1.  **Material Deduction**: This command uses the `inventory_transaction_stub` to mechanically remove items from the `inventory_state`.
2.  **Safe Failure**: If the player has insufficient repair materials, the transaction is rejected atomically. This reinforces the "Compounding Maintenance" principle where progress is gated by resource sustainability.
3.  **Audit Trail**: Each execution produces an `InventoryTransaction` record, allowing for the review of the "net economy" in console transcripts.

## Boundedness Rules

To maintain engine integrity and scope containment:

*   **No Durability Restoration (Yet)**: In the MVP phase, this command *only* drains the resource. It does not yet restore equipment durability. This allows for testing the economic drain before the full repair runtime is implemented.
*   **No Consequence Bypass**: Possessing materials does not prevent the consequences of `DEFEAT_DROP`.
*   **Atomic Transactions**: All deductions are all-or-nothing, preventing inventory corruption.

## Future Path

In future patches, this command will be coupled with equipment durability runtime. The player will execute the `repair` command to "pay" the cost of restoring an item's durability, closing the loop between wealth generation (loot) and structural upkeep.
