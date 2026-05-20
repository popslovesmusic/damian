# Console Combat Durability Decay Integration

This document explains the integration of equipment durability decay into the `combat` command within the MVP Text Console.

## Overview

The `combat` command now materiallydeteriorates a player's equipment condition after every encounter. By persisting gear state within the console session, the system turns "Equipment Pressure" into a physical strategic burden that must be addressed through the `repair` command.

## Integration Flow

1.  **Loadout Persistence**: The console session state now initializes and stores an `equipment_loadout` (loaded from `engine/equipment/contracts/example_equipment_loadout.json` if not present in the context).
2.  **Material Decay**: Following a combat encounter, the `combat_resolution_stub` calculates and applies durability loss to the loadout based on combat intensity and capacity pressure.
3.  **State Update**: The **updated** equipment loadout is persisted back into the `session_state`, ensuring that subsequent encounters operate on the deteriorated condition.
4.  **Payload Reporting**: The command payload includes detailed evidence of the wear, specifically:
    *   `durability_decay_applied`: Boolean confirmation of the deterioration.
    *   `durability_events`: Detailed records of loss for every equipped item.
    *   `updated_equipment_loadout`: The new state of the gear.
    *   `durability_pressure_observed`: True if the wear was significant.

## Boundedness and Safety

*   **No Bypass**: Equipment deterioration is a consequence of combat that does not bypass the `mvp_outcome_pipeline` or the generation of residue.
*   **Zero-Floor Boundary**: Durability is clamped at `0`. Items at zero durability report no further loss and do not disappear from the inventory, preserving their identity for future repair.
*   **Audit Trail**: Every material change is captured in structured payloads and future transcripts, ensuring the "compounding maintenance" cycle is fully reviewable.

## Strategic Impact

By persisting equipment condition across console commands, the "Tower" forces the player into a material maintenance loop. A player who ignores durability decay will eventually operate with broken gear, potentially increasing the strategic risk of future encounters until they execute the `repair` command to pay the material cost of maintenance.
