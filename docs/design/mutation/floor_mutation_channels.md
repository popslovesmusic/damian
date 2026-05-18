# Tower Engine Floor Mutation Channel Registry

This document defines the canonical registry of floor mutation channels within the Tower Engine. These channels govern how replayed floors can dynamically evolve, ensuring they remain recognizable and playable while adapting to player actions and accumulated residue.

## Core Principles

*   **Engine-Level Governance:** Mutation channels are defined at the engine level, providing a consistent framework for all content packs.
*   **Preservation of Identity:** All mutations, regardless of channel, must adhere to the principle of preserving the floor's core identity. The goal is evolution, not complete replacement.
*   **Guaranteed Playability:** Mutations must never render a floor unplayable (e.g., by creating inescapable traps or impossible combat scenarios).
*   **Content Pack Extensibility:** While core channels are engine-defined, content packs may extend the types of mutations within these channels, but not redefine the channels themselves.
*   **Decoupled Implementation:** This registry defines *what* mutations can occur. The actual algorithms for *how* mutations are chosen and applied are external to this definition.

## Floor Mutation Channels (`floor_mutation_channel_registry.json`)

The following are the defined channels through which floors can be mutated. Each channel targets a specific aspect of the floor experience.

### Channels:

*   **`layout`**:
    *   *Description*: Alters routes, doors, corridors, room accessibility, and structural topology while preserving floor recognizability.
    *   *Allowed Examples*: `collapsed_corridor`, `opened_shortcut`, `sealed_room`, `shifted_hallway`.
*   **`enemy_ecology`**:
    *   *Description*: Alters enemy composition, migration, elite presence, and behavioral pressure.
    *   *Allowed Examples*: `ash_resistant_enemies`, `predator_migration`, `elite_density_increase`, `echo_spawn`.
*   **`hazards`**:
    *   *Description*: Alters environmental hazards and traversal risks.
    *   *Allowed Examples*: `fire_vents`, `corruption_pools`, `unstable_floor_tiles`, `darkness_zones`.
*   **`loot`**:
    *   *Description*: Alters reward distribution and relic emergence.
    *   *Allowed Examples*: `hidden_cache`, `corrupted_relic`, `rare_drop_bias`, `abandoned_supply`.
*   **`easter_eggs`**:
    *   *Description*: Introduces or alters hidden survivor marks, echoes, and discoverable secrets.
    *   *Allowed Examples*: `survivor_mark_spawn`, `ghost_cache`, `echo_message`, `hidden_symbol_variant`.
*   **`story_echoes`**:
    *   *Description*: Injects persistent narrative traces from previous runs or failures.
    *   *Allowed Examples*: `fallen_adventurer_remains`, `repeated_last_words`, `memory_projection`, `boss_echo`.
*   **`stability`**:
    *   *Description*: Adjusts floor coherence, visibility, corruption pressure, and mutation intensity.
    *   *Allowed Examples*: `reduced_visibility`, `increased_instability`, `coherence_pulse`, `mutation_decay`.

## Floor Mutation Event Contract (`floor_mutation_event.schema.json`)

This JSON Schema defines the standardized structure for a `Floor Mutation Event` — a record of specific mutations applied to a floor. This contract ensures that all mutation events are well-formed and contain the necessary information for auditing and game state consistency.

### Key Fields:

*   `mutation_event_id`: Unique identifier for the event.
*   `floor_id`: The specific floor to which mutations were applied.
*   `source_outcome`: The outcome that triggered the mutation.
*   `triggering_residue_id`: Reference to the residue record that informed this mutation.
*   `applied_channels`: List of `channel_id`s that saw mutations.
*   `mutations`: An array of individual mutation objects, each specifying:
    *   `channel_id`: The channel this mutation belongs to.
    *   `mutation_id`: A specific identifier for the mutation (e.g., `collapsed_corridor`).
    *   `severity`: An integer (1-5) indicating the impact of the mutation.
    *   `preserves_floor_identity`: Boolean, `true` if this specific mutation respects the floor identity rule.
    *   `preserves_playability`: Boolean, `true` if this specific mutation respects the floor playability rule.
*   `floor_identity_preserved`, `playability_preserved`: Overall status flags for the entire event.
*   `mutation_timestamp`: When the event occurred.

## Validation and Integrity

The validation script (`tests/validate_floor_mutation_registry.py`) ensures:
*   The `floor_mutation_channel_registry.json` is well-formed and meets minimum structural requirements (e.g., at least 7 channels, all required fields).
*   The `floor_mutation_event.schema.json` is a valid JSON Schema.
*   The `example_floor_mutation_event.json` successfully validates against the `floor_mutation_event.schema.json`.
*   Specific design principles, such as all example mutations preserving floor identity and playability, are upheld.
*   The existence of specific channels like `easter_eggs` and `story_echoes` is confirmed.
*   A key rule: "No mutation channel fully replaces a floor" is conceptually validated (as this is a design principle).
