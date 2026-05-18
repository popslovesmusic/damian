# Tower Engine Persistence Design: Tower State and Floor Memory

This document outlines the schema and design principles for how the Tower Engine persists game state, including long-term tower memory and per-floor records. This persistence system is designed to allow the Tower to evolve dynamically based on player actions, failures, and successes.

## Core Principles

*   **Engine-Level Schemas:** All persistence schemas are defined at the engine level and cannot be overridden by content packs. This ensures data integrity and consistency across all titles using the Tower Engine.
*   **Data-Driven Evolution:** The Tower's state (including floor mutations and residue accumulation) is driven by persistent data, allowing for complex emergent gameplay without modifying core engine logic.
*   **Replayability and Dynamic Difficulty:** The system records enough information (residue, mutations) to allow the Tower to react to player performance, potentially adjusting difficulty or introducing new challenges in subsequent runs.
*   **Content Pack Separation:** While content packs provide the definitions for enemies, items, etc., they do not define or directly override the core persistence schema. They interact with it through defined interfaces.

## Tower State (`tower_state.schema.json`)

This schema validates the overarching, persistent memory of the entire Tower. It tracks global statistics, player progress, and overall environmental changes.

### Key Fields:

*   `tower_state_id`: Unique identifier for this specific tower's save state.
*   `engine_version`: The engine version that last saved this state, crucial for migration.
*   `content_pack_id`: The identifier of the content pack (e.g., "damian") this tower state belongs to. This ensures content-specific data can be properly loaded.
*   `current_floor`: The last known floor the player was on.
*   `highest_floor_reached`: The furthest the player has progressed.
*   `total_runs`, `total_deaths`: Global statistics for the tower.
*   `floor_memory`: An array of `floor_memory` records, detailing each floor's history.
*   `global_residue`: An object containing aggregated residue data that can influence future floor generation or global mutations.
*   `last_outcome`: The outcome of the most recent floor attempt (e.g., `DEFEAT_DROP`).
*   `updated_at`: Timestamp for the last save operation.

## Floor Memory (`floor_memory.schema.json`)

This schema validates individual records for each floor within the Tower, capturing its history and dynamic properties.

### Key Fields:

*   `floor_id`: The unique identifier for a specific floor.
*   `visit_count`, `death_count`, `victory_count`: Statistics specific to this floor.
*   `stability`, `deviation`: Metrics influencing how this floor might generate or mutate in subsequent visits. Values range from 0.0 to 1.0.
*   `mutation_level`: The current level of mutation affecting this floor.
*   `known_layout_seed`: The seed used to generate the floor's layout, ensuring it can be reproduced.
*   `active_mutations`: A list of specific mutations currently applied to this floor (e.g., "collapsed_side_corridor").
*   `discovered_easter_eggs`, `unclaimed_easter_eggs`: Arrays to track hidden content status.
*   `residue_history`: An array of `residue_record` entries, detailing events from previous visits.

## Residue Record (`residue_record.schema.json`)

This schema validates individual records of events that contribute to "residue" – data points captured after a floor outcome that can influence future mutations or tower state.

### Key Fields:

*   `residue_id`: Unique identifier for this specific residue event.
*   `floor_id`: The floor where this residue was generated.
*   `outcome`: The outcome of the floor that led to this residue.
*   `dominant_damage_type`, `most_used_skill`: Examples of gameplay metrics captured.
*   `clear_time_seconds`, `exploration_percent`: Performance metrics.
*   `party_size`: Number of players involved in the floor attempt.
*   `death_event`: Boolean indicating if a player death occurred.
*   `mutation_triggered`: Boolean indicating if this outcome directly triggered a tower mutation.
*   `notes`: Additional descriptive notes for specific residue events.

## Validation and Integrity

The validation script (`tests/validate_tower_state_schema.py`) ensures that these schemas are consistent and that example data (like `example_tower_state.json`) adheres to them, preventing invalid save states and maintaining the integrity of the Tower's persistent memory. It also enforces rules like `current_floor <= highest_floor_reached` and confirms that `DEFEAT_DROP` outcomes correctly mark `mutation_triggered`.
