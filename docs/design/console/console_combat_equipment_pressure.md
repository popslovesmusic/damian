# Console Combat Equipment Pressure Integration

This document explains how equipment pressure is integrated into the `combat` command within the MVP Text Console.

## Overview

The `combat` command now incorporates a player's equipment loadout to calculate operational pressure during encounters. This ensures that gear selection is a strategic decision involving tradeoffs between power, visibility, and upkeep cost.

## Integration Flow

1.  **Loadout Acquisition**: The console attempts to load an example bounded equipment loadout from `engine/equipment/contracts/example_equipment_loadout.json`.
2.  **Pressure Calculation**: The `equipment_pressure_stub` is used to calculate aggregate pressure (Repair, Visibility, Affinity, Capacity, Risk) from the loadout.
3.  **Session Initialization**: Both the `equipment_loadout` and the calculated `equipment_pressure` are passed to `mvp_combat_resolution_stub.make_combat_session`.
4.  **Resolution**: The combat resolution stub uses this pressure to bias outcomes (e.g., high risk gear increasing defeat risk) and report equipment-driven observations.
5.  **Payload Reporting**: The final command payload includes detailed evidence of how the equipment influenced the encounter.

## Command Payload Additions

The `combat` command payload now includes:

*   **`equipment_loadout`**: The specific gear used during the session.
*   **`equipment_pressure`**: The aggregate pressure profile (averages) derived from the gear.
*   **`equipment_pressure_used`**: A boolean confirming the integration was active.
*   **`repair_pressure_observed`**: True if gear upkeep was a significant factor.
*   **`equipment_residue_visibility_observed`**: True if gear increased the player's visibility to the Tower.
*   **`equipment_mutation_affinity_observed`**: True if the gear was sensitive to floor instability.

## Boundedness and Safety

*   **Fixed Example**: For the MVP console, a standard bounded example loadout is used to ensure stability and predictability.
*   **No Bypass**: Equipment cannot bypass core engine rules (Residue, Mutation, Defeat).
*   **Observability**: All equipment influence is reported in the structured payload and future transcripts for auditing.
