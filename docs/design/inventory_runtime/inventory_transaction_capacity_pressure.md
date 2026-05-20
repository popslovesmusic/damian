# Inventory Transaction Capacity Pressure Integration

This document explains the integration of material capacity pressure into inventory transactions.

## Overview

The inventory system now couples material transactions (adding loot, consuming items) with the strategic burden of "bag space." Every change to the inventory state automatically triggers a recalculation of capacity pressure, ensuring that the player's material wealth remains a tangible estratégico tradeoff.

## Integration Rules

1.  **Accumulated Calculation**: Unlike "Equipment Pressure," which averages profiles, capacity pressure **accumulates** material burden. It measures the ratio of `used_capacity` (sum of item costs) to the hard `inventory_capacity` limit.
2.  **Continuous Reporting**: Every `InventoryTransaction` result includes a `capacity_pressure_summary`. This provides a record of how the transaction affected the player's strategic flexibility.
3.  **Safe Failure (Strategic Bottleneck)**: If a transaction (specifically `ADD_LOOT`) would cause the `used_capacity` to exceed the `inventory_capacity`, the transaction is rejected. This enforces material strategic limits without needing a real-time encumbrance system.
4.  **Banded Categorization**: To make the burden reviewable in transcripts, pressure is categorized into discrete strategic bands (e.g., LOW, MODERATE, HIGH).

## Transaction Examples

*   **Successful Add**: Adding 10 materials to a 40-capacity bag increments the pressure from 0.0 to 0.25 (LOW band).
*   **Failed Add**: Attempting to add 15 items to a bag with only 5 remaining slots fails safely. The transcript records the failure reason and the pre-transaction pressure.
*   **Consumption**: Using a potion reduces the item count and mechanically lowers the capacity pressure, "freeing up" strategic flexibility for new loot.

## Observability

By integrating this calculation into the transaction stub, the "net economy" of the Tower becomes fully measurable. Auditors can verify if a player's successful run was achieved while operating under the stress of high capacity pressure, or if they were forced to retreat due to a lack of supplies and space.
