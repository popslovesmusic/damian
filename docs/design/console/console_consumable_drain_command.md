# Console Consumable Drain Command

This document explains the implementation of the `potion` command in the MVP Text Console, which enables the material consumption of resources from the player's inventory.

## Overview

The `potion` command bridges the gap between reported resource pressure and actual strategic burden. By allowing the player (or automated script) to explicitly consume items, the system turns abstract maintenance costs into material deductions from a bounded inventory.

## Command Behavior

*   **`potion`**: Consumes exactly one `ash_potion_small` from the current inventory.
*   **`potion <quantity>`**: Consumes the specified integer quantity of potions.

### Strategic Integration

1.  **Material Deduction**: Unlike previous stages where potion use was only "reported," this command uses the `inventory_transaction_stub` to mechanically remove items from the `inventory_state`.
2.  **Safe Failure**: If the player has fewer potions than requested, the transaction is rejected atomically. No items are consumed, and an error is reported. This forces the player to manage their supplies carefully before entering high-pressure floors.
3.  **Audit Trail**: Each use of a potion produces an `InventoryTransaction` record, which is captured in console transcripts for post-session review of economic health.

## Boundedness Rules

To maintain engine integrity and scope containment:

*   **No Real Healing**: In the MVP phase, this command *only* drains the resource. It does not actually modify a "live" health stat or provide mechanical recovery in real-time.
*   **No Consequence Bypass**: Having an abundance of potions cannot prevent the consequences of `DEFEAT_DROP` or bypass the generation of residue.
*   **Atomic Transactions**: All deductions are all-or-nothing, preventing inventory corruption or negative quantities.

## Example Integration

When the `combat exhausted` command reports that 30 potions were "used," the auditor can verify if the player actually executed enough `potion` commands to account for that pressure, or if the maintenance phase will fail due to supply exhaustion.
