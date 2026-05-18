# Tower Engine Residue Capture Taxonomy and Mutation Input Contract

This document defines the structured approach for capturing player and session behaviors as "residue" within the Tower Engine, and how this residue is then formalized into a contract for driving future floor mutations. This system is crucial for enabling the Tower to dynamically adapt and evolve based on player interactions.

## Core Principles

*   **Engine-Level Definition:** The residue taxonomy and mutation input contract are core engine components, ensuring consistency and predictability across all game titles utilizing the Tower Engine.
*   **Data-Driven Mutation:** Mutations are not hardcoded but are intelligently derived from accumulated residue, promoting emergent gameplay and dynamic tower evolution.
*   **Decoupling of Capture and Effect:** This patch defines *what* is captured and *how* it's presented to the mutation system, but explicitly *does not* implement the algorithms for how mutations are calculated or applied.
*   **Content Pack Integration:** Content packs can reference and contribute to residue categories but cannot redefine the core contract, maintaining engine integrity.

## Residue Capture Taxonomy (`residue_capture_taxonomy.json`)

This taxonomy categorizes the types of player and session data that the Tower Engine captures as residue. Each category groups related "signals" that provide granular insights into player behavior and game outcomes.

### Categories:

*   **`outcome_residue`**: Captures the final result of a floor attempt (e.g., victory, defeat, retreat).
    *   *Signals*: `last_outcome`, `death_event`, `victory_event`, `retreat_event`.
*   **`combat_residue`**: Summarizes combat-related activities (e.g., damage dealt, skills used). This focuses on behavior, not specific combat mechanics.
    *   *Signals*: `dominant_damage_type`, `most_used_skill`, `damage_taken_total`, `damage_dealt_total`, `elite_kills`, `boss_attempts`.
*   **`movement_residue`**: Tracks player movement and navigation patterns within a floor.
    *   *Signals*: `rooms_entered`, `corridors_traversed`, `dash_count`, `backtrack_count`, `time_stationary_seconds`.
*   **`exploration_residue`**: Measures the extent and nature of player exploration.
    *   *Signals*: `exploration_percent`, `hidden_rooms_found`, `easter_eggs_discovered`, `easter_eggs_claimed`, `unclaimed_easter_eggs`.
*   **`loot_residue`**: Records how players interact with loot and resources.
    *   *Signals*: `items_collected`, `items_ignored`, `rarity_highest_collected`, `relics_claimed`, `gold_collected`.
*   **`party_residue`**: Captures data relevant to multiplayer sessions, even without full network implementation.
    *   *Signals*: `party_size`, `revives_performed`, `party_downs`, `shared_defeat`, `disconnect_count`.
*   **`floor_stability_residue`**: Reflects the dynamic state and history of a specific floor.
    *   *Signals*: `visit_count`, `death_count`, `victory_count`, `stability`, `deviation`, `mutation_level`.

## Mutation Input Contract (`mutation_input_contract.schema.json`)

This JSON Schema defines the standardized structure for data payloads that are fed into the mutation system. This contract ensures that any residue-derived input to the mutation process is valid and consistent, regardless of its origin.

### Key Fields:

*   `mutation_input_id`: A unique identifier for this specific mutation request.
*   `tower_state_id`, `content_pack_id`, `floor_id`: Contextual identifiers for the current game state.
*   `source_outcome`: The specific outcome that triggered this potential mutation (e.g., `DEFEAT_DROP`).
*   `residue_summary`: A condensed summary of relevant residue data, ready for mutation logic consumption. This includes metrics like `dominant_damage_type`, `exploration_percent`, `party_size`, `death_count`, `visit_count`, `stability`, `deviation`, and `mutation_level`.
*   `eligible_mutation_channels`: An array of strings indicating which types of mutations are currently possible or allowed based on the context (e.g., `layout`, `enemy_ecology`, `easter_eggs`).
*   `mutation_constraints`: An object defining high-level rules that the mutation process must adhere to (e.g., `must_preserve_floor_identity`, `must_remain_playable`, `may_increase_difficulty`, `may_reveal_rewards`).

## Example Mutation Input (`example_mutation_input.json`)

This file provides a concrete example of a valid payload that conforms to the `mutation_input_contract.schema.json`. It demonstrates how summarized residue from a specific game state (e.g., a `DEFEAT_DROP` on floor 2) is structured for input into the mutation system.

## Validation and Integrity

The validation script (`tests/validate_residue_capture_contract.py`) ensures:
*   The `residue_capture_taxonomy.json` is well-formed and meets minimum structural requirements.
*   The `mutation_input_contract.schema.json` is a valid JSON Schema.
*   The `example_mutation_input.json` successfully validates against the `mutation_input_contract.schema.json`.
*   Specific design principles, such as the inclusion of `easter_eggs` in eligible channels and appropriate `mutation_constraints`, are met.
