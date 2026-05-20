# Combat Room Route Bias Integration

This document explains how granular room traversal routes and their associated environmental hazards bias combat outcomes within the Tower Engine.

## Overview

In the Tower Engine, tactical combat is topologically grounded. The specific route chosen by the player (e.g., a "Pressure Route" vs. a "Recovery Route") materially influences the difficulty and results of individual encounters. This ensures that spatial navigation is as consequential as resource management.

## Topological Bias Factors

The combat resolution system now incorporates the following room-route evidence:

1.  **Route Exposure**: Acts as a general hazard multiplier. High exposure routes increase effective pressure, making victory harder to achieve.
2.  **Enemy Exposure**: A component of the route's environmental profile. High local enemy density materially increases the risk of `DEFEAT_DROP` when the player is already under stress.
3.  **Resource Drain**: Routes with high resource attrition (e.g., hazardous terrain) can set `resource_pressure_observed` to true, simulating the increased supply usage needed to survive the path.
4.  **Mutation Scarring**: Unstable or scarred routes increase the visibility of the player's strategy, setting `residue_pressure_observed` to true.
5.  **Escape Modifier**:
    *   **Positive Modifiers**: Found on "Recovery" or "Escape" routes. They support tactical retreats, allowing the player to safely flee back to the Hub earlier if needed.
    *   **Negative Modifiers**: Found on "Pressure" routes. They represent constricted or trapped environments, increasing the danger of being cornered and pushed toward a defeat.

## Identity and Safety

*   **Bounded Biases**: All room-route biases are strictly bounded and cannot create impossible outcomes or bypass anti-inflation rules.
*   **Pipeline Integrity**: Topological biases only influence the *choice* of outcome. Every result is still processed through the `mvp_outcome_pipeline`, ensuring that residue and progression consequences are correctly applied.
*   **Audit Trail**: Every route-based bias is recorded in the `room_route_bias_reasoning` array, ensuring that spatial tactical decisions are fully auditable in session transcripts.

## Strategic Significance

By coupling topological choice and combat, the "Tower" creates a unified strategic map. A player must weigh the potential rewards of a hazardous "Pressure Route" against the material risk of a more difficult battle and higher supply usage. This reinforces the core principle that every spatial decision carries a physical and auditable consequence.
