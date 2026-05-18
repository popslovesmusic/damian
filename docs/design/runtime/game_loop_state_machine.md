# Tower Engine Runtime Game Loop State Machine

This document formally defines the runtime game loop as a state machine for the Tower Engine. It outlines the allowed states and the valid transitions between them, ensuring a predictable and well-structured game flow.

## States

The following states represent distinct phases within the game's runtime loop:

| State ID                      | Description                                                                 |
| :---------------------------- | :-------------------------------------------------------------------------- |
| `BOOT_ENGINE`                 | Engine initializes core manifests, schemas, and system registry.            |
| `LOAD_CONTENT_PACK`           | Selected game content pack is loaded and validated.                         |
| `LOAD_PLAYER_PROFILE`         | Player progression, inventory, and profile data are loaded.                 |
| `LOAD_TOWER_STATE`            | Persistent tower memory and floor history are loaded.                       |
| `SELECT_TARGET_FLOOR`         | Runtime determines which floor the player or party will enter.              |
| `GENERATE_OR_RESTORE_FLOOR`   | Runtime either generates a new floor or restores a previously visited floor. |
| `APPLY_RESIDUE_MUTATIONS`     | Floor is altered according to accumulated residue and mutation rules.       |
| `SPAWN_PLAYERS`               | Player entities are placed into the active floor.                           |
| `SPAWN_ENCOUNTERS`            | Enemies, hazards, events, and hidden marks are instantiated.                |
| `ACTIVE_FLOOR_LOOP`           | Main playable loop for movement, combat, loot, interaction, and exploration.|
| `RESOLVE_FLOOR_OUTCOME`       | Runtime determines victory, retreat, defeat, disconnect, or unresolved exit.|
| `WRITE_RESIDUE`               | Runtime records actions, deaths, damage patterns, exploration, and floor outcome. |
| `MUTATE_TOWER_STATE`          | Persistent tower state is updated using residue and outcome rules.          |
| `SAVE_RUNTIME_STATE`          | Player profile, tower memory, and relevant session data are persisted.      |
| `RETURN_TO_HUB_OR_NEXT_FLOOR` | Runtime routes the player to hub, next floor, previous floor, retry, or exit. |
| `SHUTDOWN_ENGINE`             | Runtime exits cleanly.                                                      |

## Transitions

The following represent the required and valid transitions between states:

*   `BOOT_ENGINE` -> `LOAD_CONTENT_PACK`
*   `LOAD_CONTENT_PACK` -> `LOAD_PLAYER_PROFILE`
*   `LOAD_PLAYER_PROFILE` -> `LOAD_TOWER_STATE`
*   `LOAD_TOWER_STATE` -> `SELECT_TARGET_FLOOR`
*   `SELECT_TARGET_FLOOR` -> `GENERATE_OR_RESTORE_FLOOR`
*   `GENERATE_OR_RESTORE_FLOOR` -> `APPLY_RESIDUE_MUTATIONS`
*   `APPLY_RESIDUE_MUTATIONS` -> `SPAWN_PLAYERS`
*   `SPAWN_PLAYERS` -> `SPAWN_ENCOUNTERS`
*   `SPAWN_ENCOUNTERS` -> `ACTIVE_FLOOR_LOOP`
*   `ACTIVE_FLOOR_LOOP` -> `RESOLVE_FLOOR_OUTCOME`
*   `RESOLVE_FLOOR_OUTCOME` -> `WRITE_RESIDUE`
*   `WRITE_RESIDUE` -> `MUTATE_TOWER_STATE`
*   `MUTATE_TOWER_STATE` -> `SAVE_RUNTIME_STATE`
*   `SAVE_RUNTIME_STATE` -> `RETURN_TO_HUB_OR_NEXT_FLOOR`
*   `RETURN_TO_HUB_OR_NEXT_FLOOR` -> `SELECT_TARGET_FLOOR`
*   `RETURN_TO_HUB_OR_NEXT_FLOOR` -> `SHUTDOWN_ENGINE`

## Outcome Modes

The `RESOLVE_FLOOR_OUTCOME` state can lead to various outcomes, which influence subsequent state transitions and data modifications:

*   `VICTORY_ASCEND`: Player successfully completes a floor. Effect: `target_floor = current_floor + 1`.
*   `DEFEAT_DROP`: Player is defeated on a floor. Effect: `target_floor = max(1, current_floor - 1); returned_floor_mutates = true`.
*   `RETREAT_TO_HUB`: Player chooses to retreat. Effect: `target_floor = hub; residue_written = partial`.
*   `SESSION_DISCONNECT`: Player disconnects. Effect: `save_runtime_state = required; floor_outcome = unresolved`.
*   `EXIT_GAME`: Player exits the game. Effect: `route_to_shutdown = true`.

## Rules

*   **No Combat/Floor Generation/Multiplayer Implementation:** This definition focuses purely on the state machine logic; no concrete implementation for these systems is included at this stage.
*   **Engine-Level State Machine:** The state machine is a core engine component and cannot be overridden by content packs.
*   **Content Pack Separation:** Content packs must not define or modify the engine's runtime loop.
