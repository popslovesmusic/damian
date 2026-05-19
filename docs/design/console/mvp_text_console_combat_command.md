# MVP Text Console Combat Command Integration

## Overview
The `combat` command integrates the deterministic **MVP Combat Resolution Stub** into the manual text console harness. This allows users to simulate combat encounters and observe how different combat pressures (enemy pressure, resource drain) affect the project's outcome pipeline.

## Command Usage
The `combat` command supports several variants to simulate different encounter scenarios:

- `combat safe`: Simulates a low-pressure encounter. Typically results in `VICTORY_ASCEND`.
- `combat dangerous`: Simulates a high-pressure encounter where the player has low health. Typically results in `DEFEAT_DROP`.
- `combat exhausted`: Simulates an encounter with high resource drain. Typically results in `RETREAT_TO_HUB`.
- `combat`: Defaults to the `safe` variant.

## Integration Logic
When the `combat` command is executed, the console runtime performs the following steps:

1.  **Build Session**: Creates a `CombatSession` object using the current `tower_state` and `player_progression`.
2.  **Resolve Outcome**: Uses `mvp_combat_resolution_stub` to determine the deterministic outcome based on the variant's pressure parameters.
3.  **Pipeline Routing**: Feeds the resolved outcome (`VICTORY_ASCEND`, `DEFEAT_DROP`, or `RETREAT_TO_HUB`) into the `mvp_outcome_pipeline`.
4.  **State Update**: Updates the console's internal session state with the new `tower_state`.
5.  **Side Effects**: If the outcome is `DEFEAT_DROP`, the pipeline triggers floor mutations and attaches survivor marks, which are then reviewable via the `diff` and `marks` commands.

## Constraints
- **Non-Real-Time**: Combat resolution is instantaneous and state-driven.
- **Pipeline Integrity**: The command does **not** bypass the residue writer or mutation systems. All outcomes flow through the standard project loops.
- **Safe Failures**: If the combat stub or pipeline dependencies are missing, the command fails gracefully with a structured error.
