# Minimal Domain Dashboard Snapshot Builder

This document explains the deterministic domain dashboard snapshot builder implementation for the Tower Engine MVP.

## Overview

The `domain_dashboard_snapshot_builder` is responsible for aggregating material evidence from all core subsystems—tactical combat, spatial traversal, inventory burden, and floor history—into a single, schema-compatible `DomainDashboardSnapshot`.

It serves as the **Strategic Cognition Layer**, turning the engine's complex material state into a readable report that informs player decision-making and meta-strategic oversight.

## Derivation Rules

To ensure a consistent and auditable meta-strategic state, snapshots are built using the following rules:

1.  **Pressure Summary**: Aggregates all current survival hazards (combat, traversal, escape risk, mutation, repair, capacity) into a weighted hazard profile (0.0 to 1.0).
2.  **Equipment Summary**: Counts damaged items, zero-durability "broken" gear, and remaining repair materials in the inventory.
3.  **Resource Summary**: Surfaces visible supplies, including total gold, ash potions, and rare materials.
4.  **Residue Summary**: Summarizes the recursive history of the Domain by counting triggered mutations, unclaimed marks, and logged residue events.
5.  **Recoverability Heuristic**: Evaluates if the player is in a "critical pressure" state (e.g., extremely high hazard or near-full inventory) while confirming that progress remains recoverable.

## Determinism and Uncertainty

*   **Evidence-Based**: Snapshots are derived strictly from the current known session state. They do not infer hidden future information or reveal unexplored map segments.
*   **Bounded Results**: All pressure values and item counts are strictly clamped or validated against their respective boundaries, preventing inflationary strategic risk.
*   **Operational Clarity**: The builder prioritizes making current burdens legible (e.g. "2 damaged items") rather than providing cosmetic polish.

## Integration Flow

1.  **Status Request**: The player or system requests a meta-strategic overview (e.g. via the console).
2.  **Data Collection**: The builder gathers evidence from the `inventory_state`, `equipment_loadout`, and `tower_state`.
3.  **Snapshot Building**: The builder aggregates the evidence into the structured `DomainDashboardSnapshot` record.
4.  **Validation**: The snapshot is validated against the schema to ensure audit consistency.
5.  **Cognition**: The summary is surfaced to the player, allowing for informed tactical and meta-strategic choices.

## Non-UI Boundary

This builder is strictly responsible for **generating data snapshots**. It does not handle:
*   Graphic UI rendering or overlays.
*   Drag-and-drop inventory interactions.
*   Web frontends or real-time animations.
