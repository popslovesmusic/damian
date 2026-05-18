# Tower Engine Hidden Survivor Mark and Easter Egg Reward Contract

This document formalizes the design and contracts for "Survivor Marks" and "Easter Eggs" within the Tower Engine. These hidden discoveries are intended to enrich replayed floors, providing optional engagement and rewards without impacting core progression.

## Core Principles

*   **Optionality:** Finding and claiming Survivor Marks is always optional. They should never be mandatory for critical path progression.
*   **Discoverability:** Marks must always be discoverable through in-game hints (visual, audio, environmental) and observation, not random chance or brute-force searching.
*   **Bounded Rewards:** Rewards associated with marks must be carefully balanced to avoid breaking player progression or creating "god-mode" scenarios.
*   **Engine-Level Rules:** The core rules for mark discovery, claiming, and reward integrity are engine-level to ensure consistency.
*   **Content Pack Theming:** Content packs can theme marks and their hints but cannot alter the fundamental rules of discoverability or optionality.
*   **No Random Spawns:** Marks are placed based on procedural generation rules that consider their context and discoverability, not purely random algorithms.

## Survivor Mark Registry (`survivor_mark_registry.json`)

This registry defines the canonical types of hidden survivor marks and the classes of rewards they can offer.

### Mark Classes:

*   **`visual_glyph`**: A subtle visual symbol integrated into the environment (e.g., carved into a wall).
    *   *Discoverability Modes*: `visual_hint`, `angle_visibility`, `lighting_reveal`.
*   **`audio_echo`**: A faint sound cue or whisper.
    *   *Discoverability Modes*: `proximity_audio`, `directional_audio`, `repeated_phrase`.
*   **`object_anomaly`**: A repeated or misplaced object within the environment.
    *   *Discoverability Modes*: `environmental_pattern_break`, `object_repetition`, `unusual_placement`.
*   **`residue_fracture`**: A visual distortion or unstable geometry, linked to replay-floor mutations.
    *   *Discoverability Modes*: `visual_distortion`, `interaction_prompt`, `instability_pulse`.

### Reward Classes:

*   **`minor_cache`**: Small loot, currency, or consumable.
*   **`rare_cache`**: Higher rarity loot or crafting materials.
*   **`memory_fragment`**: Lore, story echoes, or tower-memory progression.
*   **`orientation_upgrade`**: Small persistent build/progression modifier (never a "god-mode" unlock).
*   **`hidden_event_trigger`**: Triggers an optional encounter, room, or echo event.

### Global Rules:

*   `marks_must_be_optional`
*   `marks_must_have_at_least_one_hint`
*   `claimed_marks_must_be_recorded`
*   `unclaimed_marks_may_persist_or_mutate`
*   `rewards_must_be_bounded`
*   `marks_must_not_softlock_progression`

## Survivor Mark Contract (`survivor_mark.schema.json`)

This JSON Schema defines the standardized structure for individual survivor mark definitions that can be placed on a floor. This contract ensures consistency and validation of all hidden mark content.

### Key Fields:

*   `survivor_mark_id`: Unique identifier for the specific mark instance.
*   `floor_id`, `source_mutation_event_id`: Contextual information about where and how the mark appeared.
*   `mark_class_id`: References one of the defined `mark_classes`.
*   `hint_modes`: An array of strings indicating the active hints for discovery. Must have at least one.
*   `placement_context`: A description of the mark's location and environmental integration.
*   `claim_condition`: How the player interacts to claim the mark.
*   `reward_class_id`: References one of the defined `reward_classes`.
*   `reward_payload_ref`: Reference to the actual reward data.
*   `is_optional`, `is_discoverable`, `claimed`, `can_mutate_if_unclaimed`: Boolean flags for mark behavior and state.
*   `progression_break_risk`: An enum (`NONE`, `LOW`, `INVALID`) indicating the potential risk to player progression. Must never be `INVALID`.

## Example Survivor Mark (`example_survivor_mark.json`)

This file provides a concrete example of a valid survivor mark payload conforming to the `survivor_mark.schema.json`. It illustrates a `visual_glyph` mark with multiple hint modes, located in a specific context, leading to a `rare_cache` reward.

## Validation and Integrity

The validation script (`tests/validate_survivor_mark_contract.py`) ensures:
*   The `survivor_mark_registry.json` is well-formed (at least 4 mark classes, 5 reward classes, and global rules present).
*   The `survivor_mark.schema.json` is a valid JSON Schema.
*   The `example_survivor_mark.json` validates successfully against the `survivor_mark.schema.json`.
*   Specific design principles are upheld in the example, such as `is_optional`, `is_discoverable`, and a valid `progression_break_risk` (NONE or LOW).
*   The conceptual check that `orientation_upgrade` rewards are bounded and not "god-mode" unlocks is acknowledged as a design rule.
