# Minimal Escape Resolution Stub

This document explains the deterministic escape resolution stub implementation for the Tower Engine MVP.

## Overview

The `escape_resolution_stub` is responsible for resolving spatial retreat attempts into bounded strategic outcomes. It ensures that retreating from the Tower is not a "free" action, but a calculated risk that can result in varying degrees of success or failure based on the player's current material burden and path hazard.

## Resolution Rules

To ensure balanced strategic tension, escape attempts are resolved into the following outcomes based on **Escape Risk**:

1.  **ESCAPE_SUCCESS (Risk <= 0.30)**:
    *   **Mapping**: `RETREAT_TO_HUB`
    *   **Consequence**: Safe retreat achieved.
2.  **ESCAPE_PARTIAL (0.30 < Risk <= 0.60)**:
    *   **Mapping**: `RETREAT_TO_HUB`
    *   **Consequence**: Retreated successfully, but suffered a minor **Resource Loss** (e.g., small gold penalty).
3.  **ESCAPE_FAILED_PRESSURE_SPIKE (0.60 < Risk <= 0.80)**:
    *   **Mapping**: `RETREAT_TO_HUB`
    *   **Consequence**: Retreat achieved, but triggered an environmental reaction (increased mutation pressure).
4.  **ESCAPE_FAILED_RETREAT_DROP (Risk > 0.80 AND Exposure >= 0.70)**:
    *   **Mapping**: `DEFEAT_DROP`
    *   **Consequence**: Severe failure. The player is intercepted or overwhelmed during the flee attempt, suffering a floor drop and mutation as if defeated in combat.
5.  **ESCAPE_FAILED_RESOURCE_LOSS (Risk > 0.80 but low Exposure)**:
    *   **Mapping**: `RETREAT_TO_HUB`
    *   **Consequence**: Retreat achieved, but at a significant material cost (loss of gold and potions).

## Bounded Consequences

*   **Residue Preservation**: Every escape attempt, regardless of outcome, writes residue to the floor, marking the strategic "effort" of the journey home.
*   **Recoverability**: Even the most severe failure (`DEFEAT_DROP`) remains bounded. The system never deletes unique items or creates unrecoverable dead states; it only applies material and progression consequences.
*   **Auditability**: Every resolution record is captured in transcripts, allowing auditors to review the "why" of every failed retreat.

## Integration Flow

1.  **Escape Command**: The player attempts to flee (e.g., `escape` command).
2.  **Risk Assessment**: The console calculates `escape_risk` using the `traversal_pressure_stub`.
3.  **Resolution**: The `escape_resolution_stub` determines the outcome and material losses.
4.  **Pipeline Routing**: The result is executed through the `mvp_outcome_pipeline`, applying progression changes and writing residue.
5.  **Observation**: The full `EscapeResolution` record is recorded in session transcripts.

## Non-Map Boundary

This stub is strictly responsible for **resolving results**. It does not handle:
*   Real-time chase mechanics.
*   Visual pathfinding on a map.
*   Rendered character movement.
