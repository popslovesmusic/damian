# Console Repair Runtime Integration

This document explains the integration of the bounded repair runtime into the `repair` command within the MVP Text Console.

## Overview

The `repair` command has been updated to transition from a simple resource drain to a material strategic restoration. It now connects the player's material inventory (Stage 008) to their equipment's material condition (Stage 009), closing the "Compounding Maintenance" loop.

## Integration Flow

1.  **Item Selection**: The command automatically selects the first item in the player's `equipment_loadout` that has current durability less than its maximum.
2.  **Runtime Execution**: It calls the `repair_runtime_stub.apply_repair` function, passing the selected item and the current `inventory_state`.
3.  **Material Consumption**: The stub leverages the `inventory_transaction_stub` to materially deduct `repair_material_basic` from the inventory.
4.  **State Persistence**: If the repair succeeds, both the updated `equipment_loadout` (with restored durability) and the updated `inventory_state` (with deducted materials) are persisted back into the console session state.
5.  **Aggregate Recalculation**: After the repair, the aggregate operational pressure of the loadout is recalculated to reflect the improved condition.
6.  **Payload Reporting**: The command returns detailed evidence of the restoration, including the `repair_event`, the `inventory_transaction`, and the resulting capacity pressure.

## Boundedness and Safety

*   **Finite Restoration**: Each material restores exactly **10.0 points** of durability. restoration is strictly clamped to the item's maximum limit.
*   **Safe Failure**: If materials are insufficient, the command fails safely. No items are consumed, and gear condition remain unchanged.
*   **Auditability**: Every material restoration is captured in structured payloads and future transcripts, ensuring the maintenance cycle is fully observable.

## Strategic Significance

By materially connecting repairs to resources, the "Tower" forces the player to prioritize which gear to maintain. A player with limited materials must decide whether to restore their primary weapon or their protective armor, reinforcing the engine's core "strategy-driven" identity.
