# Minimal Inventory Transaction Stub

This document explains the deterministic inventory transaction stub implementation for the Tower Engine MVP.

## Overview

The `inventory_transaction_stub` provides a safe and auditable way to modify the player's inventory state. It bridges the gap between "observed" resource pressure and "material" resource burden by mechanically tracking items, gold, and capacity.

## Transaction Types

The stub supports the following atomic operations:

1.  **ADD_LOOT**: Transfers gold and materials from a `LootEvent` into the inventory.
2.  **CONSUME_ITEM**: Depletes a specific item (e.g., a potion).
3.  **DEDUCT_CURRENCY**: Removes gold or shards (used for maintenance or future shops).
4.  **CAPACITY_CHECK**: Recalculates used capacity and verifies it remains within the hard boundary.

## Safe Failure Boundaries

To ensure the integrity of the player's progress, the stub enforces "All-or-Nothing" transactions:

*   **Atomic Application**: A transaction is only applied if every sub-step succeeds. If a player lacks sufficient gold or capacity, the **entire** transaction is rejected, and the original inventory state remains untouched.
*   **No Negative Quantities**: Item counts and currency values are strictly guarded against going below zero.
*   **Capacity Enforcing**: The stub rejects any transaction that would push the `used_capacity` beyond the `inventory_capacity` limit.

## Implementation Flow

1.  **State Copying**: The stub always operates on a deep copy of the `inventory_state`.
2.  **Validation**: Every modification is validated against the internal logic and potentially the JSON schema.
3.  **Audit Trail**: Every operation produces a structured `InventoryTransaction` record, detailing the "before" and "after" states and any deltas applied.
4.  **Result Reporting**: The final result includes the updated state (on success) and a human-readable summary.

## Net Economy Enforcement

By failing safely on insufficient resources, the inventory stub turns abstract pressure into a strategic bottleneck. If a player cannot "pay" the gold cost reported by a `combat_resolution_stub`, the maintenance fails, ensuring that wealth is a tool for survival, not a passive score.
