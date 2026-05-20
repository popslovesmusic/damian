# Minimal Repair Runtime Stub

This document explains the deterministic equipment repair stub implementation for the Tower Engine MVP.

## Overview

The `repair_runtime_stub` provides a material strategically connection between the player's inventory and their equipment's condition. It allows for the bounded restoration of durability by consuming specific repair materials, closing the loop between deterioration (combat strain) and maintenance (resource cost).

## Repair Rules

To ensure game balance and maintain the MVP scope, the following rules are enforced:

1.  **Material Cost**: Repairing gear requires `repair_material_basic`. Every successful repair attempt mechanically deducts these items from the `inventory_state` using atomic transactions.
2.  **Bounded Restoration**: Each repair material restores a fixed, deterministic amount of durability (`10.0` points per material).
3.  **Maximum Clamp**: Durability can never be restored beyond an item's `maximum_durability` value.
4.  **Safe Failure**: If the player lacks the required materials, the repair fails safely. No materials are consumed, and the equipment remains in its deteriorated condition. This enforces material estratégico bottlenecks.

## Non-Repair Scope

This stub is strictly responsible for **restoration**. It does not handle:
*   Crafting new repair materials.
*   Modifying maximum durability.
*   Enabling invulnerability or removing the operational burden of gear.
*   Visual UI for repairing items.

## Integration Flow

1.  **Repair Command**: The player executes a `repair` command in the console.
2.  **State Acquisition**: The console retrieves the `inventory_state` and the target `EquipmentItem`.
3.  **Deduction & Update**: The stub calls `inventory_transaction_stub.consume_inventory_item` for the materials and calculates the new durability.
4.  **Event Recording**: Every successful repair produces a `RepairEvent` record, detailing the "before" and "after" state.
5.  **Transcript Visibility**: These events are captured in console transcripts, ensuring the maintenance cycle is fully auditable.
