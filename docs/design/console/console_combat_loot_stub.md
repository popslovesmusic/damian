# Console Combat Loot Stub Integration

This document explains how bounded loot events are integrated into the `combat` command within the MVP Text Console.

## Overview

The `combat` command has been extended to produce deterministic, bounded loot events following the resolution of a combat encounter. These rewards are schema-compatible with the future full loot system but remain strictly bounded to prevent power creep during the MVP phase.

## Integration Flow

1.  **Combat Resolution**: Combat is resolved through the `combat_resolution_stub` and the `mvp_outcome_pipeline`.
2.  **Loot Generation**: Based on the `resolved_outcome` (e.g., `VICTORY_ASCEND`, `DEFEAT_DROP`), the `mvp_loot_event_stub` is called to generate a loot event.
3.  **Payload Enrichment**: The resulting `loot_event` is attached to the command's response payload, along with a human-readable `loot_summary`.
4.  **Observability**: The payload also explicitly includes `resource_sink_pressure` and `bounded_reward_flags` to ensure economic costs and safety boundaries are visible to auditors.

## Payload Additions

The `combat` command payload now includes:

*   **`loot_event`**: The full JSON object representing the rewards and metadata.
*   **`loot_summary`**: A concise string summary of the gold and materials granted.
*   **`resource_sink_pressure`**: Estimated costs for potions, repairs, and domain upkeep associated with the encounter level.
*   **`bounded_reward_flags`**: A set of booleans confirming that no game-breaking abilities (like invulnerability) were granted.

## Boundedness Rules

*   **No Inventory Persistence**: Rewards are reported in the console transcript but not yet added to a persistent player inventory.
*   **Fixed Rewards**: Gold and material values are mapped directly to outcomes (e.g., 10,000 gold for `VICTORY_ASCEND`).
*   **Safety Flags**: All power-bypassing flags in `bounded_reward_flags` are strictly `False`.

This integration ensures that while the economy is being "simulated" through reporting, no unmanaged state is introduced into the engine core yet.
