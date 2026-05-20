# Minimal Traversal Pressure Stub

This document explains the deterministic traversal pressure stub implementation for the Tower Engine MVP.

## Overview

The `traversal_pressure_stub` provides a way to calculate the material and strategic burden of moving between floors (traversal). It turns the "journey" into a series of strategic tradeoffs where spatial choices carry material consequences.

## Calculation Rules

To ensure game balance and maintain the MVP scope, the following rules are enforced:

1.  **Deterministic Pressure**: Traversal pressure is a weighted combination of:
    *   **Combat Exposure (40%)**: The primary risk of exploration.
    *   **Mutation Pressure (30%)**: Environmental instability.
    *   **Capacity Pressure (20%)**: The material burden of held items (accumulated weight).
    *   **Repair Burden (10%)**: The wear and tear on current gear.
2.  **Escape Risk**: The risk of failing to retreat or escape increases with both the traversal pressure and the `route_exposure` of the selected path.
3.  **Material Integration**: The stub uses the `inventory_capacity_pressure` module to ensure that the physical weight of items materially impacts movement and escape.
4.  **Bounded Range**: All individual and aggregate metrics are strictly bounded between `0.0` (safe/easy) and `1.0` (extremely hazardous).

## Accumulated vs. Averaged Burden

Unlike "Equipment Pressure," which averages operational profiles to find a mean burden, **Traversal Pressure incorporates Capacity Pressure as an accumulation.** 

This means that every material loot addition materially increases the hazard of moving and the difficulty of escaping, reinforcing the core strategic tradeoff between supplies and strategic flexibility.

## Integration Flow

1.  **Route Choice**: The player decides to move between floors (e.g., `ascend` or `retreat`).
2.  **Pressure Assessment**: The console gathers current material pressures (inventory capacity, mutation level, etc.).
3.  **Event Creation**: The stub calculates the final pressure and risk, producing a `TraversalEvent` record.
4.  **Validation**: The event is validated against the schema.
5.  **Transcript Reporting**: The event is captured in structured transcripts for post-session review of spatial choices.

## Non-Movement Boundary

This stub is strictly responsible for **calculating burden**. It does not handle:
*   Real-time character movement.
*   Pathfinding across complex maps.
*   Rendering of floor layouts.
*   Animation of traversal actions.
