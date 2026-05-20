# Inventory Capacity Pressure

This document explains the implementation of inventory capacity pressure in the Tower Engine.

## Overview

Capacity Pressure is a material metric that represents the strategic burden of a player's current supplies and equipment. Unlike "Equipment Pressure," which is an average of operational profiles, **Capacity Pressure is an accumulation of material weight.** It directly measures how much of the player's finite strategic flexibility (bag space) is currently occupied.

## Calculation Rules

The pressure is calculated using a deterministic linear model:

`capacity_pressure = used_capacity / inventory_capacity`

*   **Accumulated Burden**: Used capacity is the sum of the `capacity_cost` of all items in the inventory.
*   **Bounded Values**: The pressure is strictly clamped between `0.0` (empty) and `1.0` (full).
*   **Enforced Limits**: For the MVP, any transaction that would push `used_capacity` beyond `inventory_capacity` is rejected as an invalid strategic state.

## Strategic Bands

To ensure the burden is observable and reviewable in transcripts, capacity pressure is categorized into the following bands:

| Band | Pressure Range | Strategic Meaning |
| :--- | :--- | :--- |
| **EMPTY** | `0.0` | Total strategic flexibility. |
| **LOW** | `>0.0` to `0.25` | Negligible burden. |
| **MODERATE** | `>0.25` to `0.60` | Strategic choices starting to matter. |
| **HIGH** | `>0.60` to `<1.0` | Heavy burden; flexibility severely reduced. |
| **FULL** | `1.0` | No additional supplies can be carried. |
| **INVALID** | N/A | Over-capacity or corrupted state. |

## Integration Flow

1.  **Material Change**: A transaction (loot add or potion use) modifies the item list.
2.  **Accumulation**: The `inventory_transaction_stub` recalculates the total `used_capacity`.
3.  **Pressure Calculation**: The `inventory_capacity_pressure` module translates the raw counts into a 0.0-1.0 metric.
4.  **Enrichment**: The resulting band and pressure are added to the transaction summary.
5.  **Observability**: Transcripts capture the capacity band to allow auditors to verify that the player is operating within material strategic limits.
