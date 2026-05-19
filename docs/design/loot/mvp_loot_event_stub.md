# MVP Loot Event Stub

This document explains the minimal loot event stub implementation for the Tower Engine MVP.

## Overview

The `mvp_loot_event_stub` provides a deterministic and bounded way to generate rewards from combat outcomes and survivor mark claims. It is designed to be schema-compatible with the future full loot system while maintaining strict boundaries to prevent scope creep.

## Bounded Reward Rules

To ensure game balance and maintain the MVP scope, the following rules are enforced:

1.  **Deterministic Rewards**: Rewards are mapped directly to the outcome of an event (e.g., VICTORY_ASCEND always grants the same base rewards).
2.  **Strictly Bounded**: No loot event can grant power-bypassing abilities. All `bounded_reward_flags` (e.g., `grants_invulnerability`) must remain `False`.
3.  **Resource Sink Reporting**: Every loot event reports the "Resource Sink Pressure," which estimates the costs the player is expected to incur (potions, repairs, etc.). This helps in balancing the economy by making the costs visible.

## Reward Tiers

| Outcome / Source | Gold | Stability Shards | Residue Fragments | Rare Materials |
| :--- | :--- | :--- | :--- | :--- |
| **VICTORY_ASCEND** | 10,000 | 1 | 1 | 0 |
| **DEFEAT_DROP** | 1,500 | 0 | 1 | 0 |
| **RETREAT_TO_HUB** | 500 | 0 | 0 | 0 |
| **Survivor Mark** | 2,500 | 2 | 1 | 1 |

## Integration Flow

1.  **Event Completion**: A combat session or survivor mark claim is resolved.
2.  **Loot Generation**: The relevant wrapper function (`make_combat_loot_event` or `make_survivor_mark_loot_event`) is called.
3.  **Validation**: The generated event is validated against `engine/loot/contracts/loot_event.schema.json`.
4.  **Reporting**: The loot event is included in the outcome payload for reporting and potential future persistence.
