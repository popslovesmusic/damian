# Tower Engine Bounded Player Progression and Residue Pressure

This document outlines the design philosophy and contractual agreements for player progression within the Tower Engine. The core objective is to foster a sense of meaningful, persistent player growth that enhances survivability, tactical options, and efficiency, without ever leading to a "god-mode" state that trivializes the Tower's inherent adaptive challenge and residue consequences.

## Core Principles

*   **Real Growth, Not Runaway Power:** Player progression should feel substantial, but it must always remain bounded. The Tower is designed to adapt, ensuring that increased player power is met with evolving challenges, rather than simply making the game easier.
*   **Survivability over Supremacy:** Growth primarily focuses on improving the player's capacity to survive deeper and more challenging floors, providing more tools and resilience, rather than allowing them to obliterate all threats without consequence.
*   **Residue as a Counterbalance:** The residue system (TOWER-ENGINE-004) acts as a critical pressure valve, dynamically increasing the Tower's adaptive responses to player power and tactics. Over-optimized strategies will be met with increased residue pressure, leading to mutations.
*   **Anti-God-Mode Contract:** Explicit rules and validation ensure that game systems cannot grant players abilities that negate core gameplay loops (e.g., invulnerability, infinite damage, immunity to death consequences).
*   **Content Pack Theming, Not Weakening:** Content packs can introduce unique progression paths, skills, or items, but they must always adhere to the engine's core bounded progression and anti-god-mode principles.

## Bounded Progression Rules (`bounded_progression_rules.json`)

This file contains the canonical ruleset governing player growth.

### Core Principle:

*   "Player growth improves survivability, options, efficiency, and depth access, but must not remove risk, adaptation, or residue consequences." This principle underpins all progression design.

### Allowed Growth Vectors:

These define the acceptable avenues for player development:

*   **`stat_growth`**: Incremental increases to core attributes (health, damage, defense, speed, recovery).
*   **`skill_unlocks`**: Acquisition of new active or passive abilities that expand tactical choices.
*   **`gear_progression`**: Improvement through itemization (rarity, affixes, relics, crafting).
*   **`orientation_mastery`**: Persistent refinement of a player's chosen playstyle identity (e.g., specific builds), without leading to absolute invulnerability.
*   **`tower_knowledge`**: Player's growing understanding of floor layouts, enemy behaviors, hidden mechanics, and mutation patterns.

### Forbidden Growth Results:

These outcomes are explicitly prohibited to prevent "god-mode" scenarios:

*   `permanent_invulnerability`
*   `infinite_damage_scaling`
*   `resource_cost_elimination_without_tradeoff`
*   `complete_enemy_trivialization`
*   `residue_immunity`
*   `mutation_immunity`
*   `death_consequence_immunity`
*   `guaranteed_easter_egg_detection`
*   `floor_skip_without_cost`

### Residue Pressure Checks:

Mechanisms through which player progression feeds back into the Tower's adaptive systems:

*   **`dominant_build_visibility`**: Consistent use of a single dominant strategy increases its visibility to the Tower, making it a target for adaptation.
*   **`power_use_strain`**: High-output abilities or overtuned synergies may generate increased deviation or mutation pressure.
*   **`overoptimization_response`**: Excessive reliance on a specific damage type, skill, or tactic makes the player eligible for targeted mutations.
*   **`survivability_not_supremacy`**: A constant reminder that progression is for deeper survival, not for eliminating threat.

## Player Progression State Contract (`player_progression_state.schema.json`)

This JSON Schema validates the payload representing a player's current progression state. It ensures adherence to the bounded growth and anti-god-mode principles.

### Key Fields:

*   `player_id`, `profile_id`, `content_pack_id`: Unique identifiers and contextual information.
*   `level`, `highest_floor_reached`: Core progression metrics.
*   `active_orientation`: The current build identity.
*   `stats`: Detailed core player attributes (e.g., `health`, `damage`, `defense`).
*   `unlocked_skills`, `equipped_items`: Arrays representing player capabilities.
*   `residue_pressure`: An object containing values (0.0-1.0) for `dominant_build_visibility`, `power_use_strain`, `overoptimization_pressure`.
*   `forbidden_flags`: An object of boolean flags (`permanent_invulnerability`, `infinite_damage_scaling`, etc.) that must *always* be `false` to prevent "god-mode" scenarios.

## Example Player Progression State (`example_player_progression_state.json`)

This file provides a concrete example of a valid player progression state, demonstrating a player at `level 8` with specific stats, unlocked skills, and items. Critically, all `forbidden_flags` are set to `false`, aligning with the anti-god-mode contract.

## Validation and Integrity

The validation script (`tests/validate_bounded_player_progression.py`) ensures:
*   The `bounded_progression_rules.json` exists and contains the required growth vectors, forbidden results, and residue pressure checks.
*   The `player_progression_state.schema.json` is a valid JSON Schema.
*   The `example_player_progression_state.json` validates successfully against the schema.
*   All `forbidden_flags` in the example are `false`.
*   Residue pressure values in the example are within the 0.0-1.0 bounds.
*   The conceptual rule that progression emphasizes survivability, not supremacy, is acknowledged as a design principle.
