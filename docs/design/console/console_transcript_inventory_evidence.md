# Console Transcript Inventory Evidence

This document explains how the console transcript reporting system captures and records material inventory changes during combat and exploration.

## Overview

The `console_transcript_reporter` has been extended to capture the materialization of economic pressure. Transactions that were previously abstract (reported loot events) are now mechanically applied to a persistent inventory, and the results of these transactions are recorded as reviewable evidence.

## Captured Evidence

The transcript now includes the following inventory observability fields:

*   **`inventory_transactions_observed`**: The total count of attempted inventory operations in the session.
*   **`inventory_applications_observed`**: The count of successfully applied material changes.
*   **`inventory_failures_observed`**: The count of transactions that failed safely (e.g., due to insufficient gold or capacity).
*   **`total_gold_added_to_inventory`**: The material gold accumulated into the player's inventory during the session.
*   **`items_added_to_inventory`**: A record of all items (potions, fragments) materially added to the inventory.
*   **`items_deducted_from_inventory`**: A record of all items depleted or lost.
*   **`capacity_pressure_observed`**: A boolean flag set to `True` if any transaction resulted in a non-zero inventory weight/capacity.
*   **`inventory_summaries`**: An array of structured snapshots showing the net state of gold, materials, and used capacity after key events.

## Integration Flow

1.  **Combat/Loot Event**: A console command (e.g., `combat safe`) produces a `loot_event`.
2.  **Material Transaction**: The console calls `inventory_transaction_stub.add_loot_to_inventory`.
3.  **Safe Application**: The stub attempts to modify a copy of the `inventory_state`.
4.  **Evidence Extraction**: The transcript reporter inspects the `inventory_transaction` and `inventory_state_summary` attached to the command payload.
5.  **Audit Recording**: The reporter aggregates the deltas and records safe failures for post-session review.

## Consequence Preservation

The inventory system adheres to the core engine identity: **reward does not erase consequence**. 
- **Persistence**: Gold and materials are tracked, making future repair and maintenance costs material.
- **Fail-Safe**: If a transaction would violate strategic constraints (like capacity), it fails safely without corrupting progress, reinforcing the importance of resource management.
- **No Bypass**: Inventory state cannot prevent generation of residue or the structural changes triggered by mutations.
