# Console Combat Enemy Pressure Integration

This document explains how the `combat` command in the MVP Text Console integrates with the `enemy_pressure_selector` to provide adaptive combat encounters.

## Overview

The `combat` command now uses the `enemy_pressure_selector` to select an enemy archetype and build a pressure profile based on the current floor's memory before initiating combat. This ensures that the "Tower" adapts to the player's previous performance and strategy.

## Integration Flow

1.  **Floor Memory Retrieval**: The console retrieves the `floor_memory` for the current floor from the `tower_state`.
2.  **Archetype Selection**: The `enemy_pressure_selector.select_enemy_archetype` function is called with the `floor_memory`. This function uses mutation levels, stability, and residue history to determine the most appropriate enemy archetype (e.g., `attrition_unit`, `counter_unit`).
3.  **Profile Building**: The `enemy_pressure_selector.build_enemy_pressure_profile` function creates a detailed profile including:
    *   `enemy_archetype_id`
    *   `base_pressure_rating` (derived from mutation level)
    *   `adaptation_reasoning` (human-readable explanation of why this archetype was selected)
4.  **Combat Session Initialization**: The `enemy_pressure_profile` is passed to `mvp_combat_resolution_stub.make_combat_session`.
5.  **Resolution and Reporting**:
    *   The `combat_resolution_stub` uses the profile to bias combat outcomes (e.g., higher defeat risk at low health against `ambush_unit`).
    *   The command payload includes `enemy_archetype_id`, `enemy_adaptation_reasoning`, and `enemy_pressure_profile_used` for observability and debugging.

## Command Variants

The existing command variants (`safe`, `dangerous`, `exhausted`) still set baseline `enemy_pressure_rating` and `player_health`, but the `enemy_pressure_profile` can now increase the effective pressure based on the archetype.

## Payload Additions

The `combat` command payload now includes:

*   `enemy_pressure_profile`: The complete profile used for the session.
*   `enemy_archetype_id`: The ID of the selected archetype.
*   `enemy_adaptation_reasoning`: An array of strings explaining the selection.
*   `enemy_pressure_profile_used`: A boolean confirming the integration was active.
