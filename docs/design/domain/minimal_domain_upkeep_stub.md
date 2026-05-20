# Minimal Domain Upkeep Stub

This document explains the deterministic domain upkeep stub implementation for the Tower Engine MVP.

## Overview

The `domain_upkeep_stub` provides the mechanical logic for maintaining localized стратеги footholds (Domain Claims). It materializes the "cost of order" by requiring the expenditure of "Stability Shards" to prevent foothold decay.

## Upkeep Cost Calculation

Maintenance is not a flat fee. The cost to hold territory scales based on two primary factors:

1.  **Floor Depth**: Deep-floor footholds are materially more expensive to maintain as the Tower's natural entropy is stronger.
2.  **Foothold Complexity**: High-value claims (like `survivor_outpost` or `repair_station`) require more resources than basic `recovery_anchors`.

## State Decay Machine

If a player fails to pay the required upkeep per run, the foothold transitions through a deterministic decay state machine:

*   **ACTIVE**: The foothold is well-maintained and providing full strategic benefits.
*   **DECAYING**: Upkeep was missed. Strategic benefits are reduced (materially represented by increased Visibility Pressure and future reduction in recovery effectiveness).
*   **OVERRUN**: Consecutive upkeep failures or severe environmental response have caused the foothold to fail. All strategic benefits are lost, and the node may revert to a hazardous state.

## Bounded Transactions

All upkeep operations are deterministic and bounded. The stub ensures that:
*   Upkeep costs never exceed reasonable strategic limits.
*   State transitions are strictly linear (Active -> Decaying -> Overrun).
*   Restoration (Decaying -> Active) is possible but requires the full material cost.

## Non-Spatial Boundary

This stub is strictly responsible for **calculating and transitioning claim state**. It does not handle:
*   Auto-harvesting of shards.
*   Visual rendering of ruins.
*   Physical combat defense.
