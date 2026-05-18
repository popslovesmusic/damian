# Tower Engine Floor Identity Preservation

This document defines the core rules and philosophy for preserving the identity and playability of floors within the Tower Engine when they undergo mutation. The goal is to ensure that while floors can dynamically evolve and adapt based on player actions and residue, they always remain recognizably the same floor and continue to offer a fair and traversable experience.

## Core Principles

*   **Engine-Level Governance:** Identity preservation rules are central to the engine's design, ensuring that all procedural generation and mutation systems adhere to these principles.
*   **Recognizability over Static Replication:** Mutations should enhance or alter, not erase, the distinct characteristics that make a floor unique. Players should still feel they are on "Floor X," even if it has changed.
*   **Guaranteed Playability:** A mutated floor must always be solvable and traversable. Soft-locks, unreachable areas, or impossible challenges are strictly forbidden.
*   **Content Pack Constraints:** Content packs may specify additional, theme-specific identity constraints but can never weaken the engine's core preservation rules.

## Floor Identity Preservation Rules (`floor_identity_preservation_rules.json`)

This file contains the canonical set of rules that define how floor identity and playability must be maintained across mutations.

### Required Identity Anchors:

These are fundamental aspects of a floor that must be preserved or maintain clear lineage across mutations:

*   **`layout_seed_lineage`**: Mutated floors must retain a traceable connection to their original layout seed, allowing for forensic analysis and ensuring the "essence" of the original design is not lost.
*   **`entry_exit_continuity`**: The logical connections and physical paths to and from the floor (entry and exit points) must remain valid and functional.
*   **`primary_route_survivability`**: At least one viable path from the entry point to the primary objective (e.g., the exit, a boss encounter) must always exist and be traversable.
*   **`landmark_continuity`**: Significant, recognizable landmarks or structural motifs within the floor should persist or be mutated in a way that retains their conceptual identity.
*   **`floor_theme_continuity`**: While minor aesthetic shifts are allowed, the floor's core biome, environmental theme, or architectural style must remain consistent unless explicitly designed for transformative events (which would have their own, higher-level identity rules).
*   **`difficulty_bounds`**: Mutations must not push the floor's difficulty beyond acceptable bounds, preventing scenarios that are objectively impossible or unfairly frustrating for players.
*   **`secret_discoverability`**: Any hidden content (like easter eggs or secret areas) must remain discoverable through in-game hints or logical exploration, not require random guessing or brute force.

### Forbidden Mutation Results:

These outcomes are strictly prohibited for any floor mutation:

*   `full_floor_replacement`
*   `unreachable_exit`
*   `unreachable_spawn`
*   `mandatory_softlock`
*   `all_routes_blocked`
*   `theme_replacement_without_lineage`
*   `easter_egg_without_visual_or_audio_hint`
*   `mutation_severity_without_playability_check`

### Identity Status Values:

The possible states for a floor's identity after a mutation check:

*   `PRESERVED`: The floor's identity and playability are fully intact.
*   `WEAKENED_BUT_VALID`: The floor's identity is somewhat altered but still recognizable and fully playable.
*   `FAILED`: The floor's identity or playability has been compromised.

## Floor Identity Check Contract (`floor_identity_check.schema.json`)

This JSON Schema defines the standardized structure for payloads that represent the result of an identity preservation check on a mutated floor. This contract ensures that the output from procedural generation or mutation systems provides consistent, auditable data regarding floor integrity.

### Key Fields:

*   `identity_check_id`: Unique ID for this check result.
*   `floor_id`, `original_layout_seed`, `mutated_layout_seed`, `source_mutation_event_id`: Contextual identifiers.
*   `anchors_checked`: List of `anchor_id`s that were evaluated.
*   `forbidden_results_detected`: List of `forbidden_mutation_results` that were found.
*   `entry_reachable`, `exit_reachable`, `primary_route_exists`: Booleans indicating fundamental traversability.
*   `landmark_continuity_score`, `theme_continuity_score`, `secret_discoverability_score`: Quantitative scores (0.0-1.0) for aspects of identity preservation.
*   `identity_status`: The overall identity status (`PRESERVED`, `WEAKENED_BUT_VALID`, `FAILED`).
*   `playability_preserved`: Overall boolean indicating if the floor is playable.

## Validation and Integrity

The validation script (`tests/validate_floor_identity_preservation.py`) ensures:
*   The `floor_identity_preservation_rules.json` is well-formed and contains the required number of anchors and forbidden results.
*   The `floor_identity_check.schema.json` is a valid JSON Schema.
*   The `example_floor_identity_check.json` validates successfully against the schema.
*   Specific design principles, such as `entry_reachable`, `exit_reachable`, `primary_route_exists`, and `playability_preserved` being true in the example, are upheld.
*   The example's `identity_status` is either `PRESERVED` or `WEAKENED_BUT_VALID`.
