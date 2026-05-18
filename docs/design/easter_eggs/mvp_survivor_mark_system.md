# MVP Hidden Survivor Mark System

## Overview

This document describes the Minimal Viable Prototype (MVP) Hidden Survivor Mark System. This system provides a basic framework for creating, attaching, discovering, and claiming special "survivor marks" that can appear on floors. In the MVP context, these marks are primarily attached to floors that have undergone replay mutation, offering players a mechanism to find hidden rewards and explore consequences of mutations.

## Purpose

The primary objectives of this system are:
1.  **Introduce Discoverability**: Provide an optional layer of discoverable content within mutated floors.
2.  **Bounded Rewards**: Offer minimal, balanced rewards that do not break player progression or create "god-mode" scenarios.
3.  **Integration with Mutation**: Demonstrate how dynamic floor changes (mutations) can lead to new, interactive elements.
4.  **Proof of Concept**: Establish the technical foundation for more complex easter egg and hidden content systems.

## Key Functions

-   **`make_survivor_mark(floor_id, source_mutation_event_id='unknown_mutation', mark_index=1, debug=False)`**:
    Creates a new survivor mark record for a given `floor_id`, optionally linking it to a `source_mutation_event_id`. Marks are generated with default properties (optional, discoverable, low progression risk).
-   **`attach_survivor_mark_to_floor_memory(floor_memory, survivor_mark, debug=False)`**:
    Adds a `survivor_mark_id` to the `unclaimed_easter_eggs` list within a specific `floor_memory` record.
-   **`discover_survivor_mark(floor_memory, survivor_mark_id, debug=False)`**:
    Simulates the discovery of a mark. It moves the `survivor_mark_id` from the `unclaimed_easter_eggs` list to the `discovered_easter_eggs` list in the `floor_memory`.
-   **`claim_survivor_mark(floor_memory, survivor_mark_id, debug=False)`**:
    Simulates claiming a discovered mark. It removes the `survivor_mark_id` from the `discovered_easter_eggs` list and returns a structured, bounded reward placeholder.
-   **`list_unclaimed_survivor_marks(floor_memory)`**:
    Returns a list of `survivor_mark_id`s that are present in the `unclaimed_easter_eggs` list of a given `floor_memory`.

## Default Mark Behavior

-   **`mark_class_id`**: "visual_glyph" (a generic visual indicator).
-   **`hint_modes`**: Includes "visual_hint" and "lighting_reveal" to suggest discoverability.
-   **`reward_class_id`**: "rare_cache" (a placeholder for a valuable but not game-breaking reward).
-   **`is_optional`**: `true` (players are not required to find marks).
-   **`is_discoverable`**: `true` (marks are intended to be found through gameplay hints).
-   **`claimed`**: `false` (initial state).
-   **`can_mutate_if_unclaimed`**: `true` (marks can be affected by subsequent mutations if not found).
-   **`progression_break_risk`**: "LOW" (rewards are balanced not to disrupt core progression).

## Claim Behavior

-   A successfully claimed mark is removed from `floor_memory["discovered_easter_eggs"]`.
-   Attempting to claim the same mark twice (or a mark that hasn't been discovered) will fail safely.
-   Claiming a mark returns a generic, bounded reward placeholder (e.g., a "rare_cache" with a randomized, limited value).
-   Rewards explicitly do not grant "god-mode" advantages or otherwise break progression balance.

## Dependencies

-   `engine.debug.runtime.debug_logger`: For structured debug logging.
-   `engine.save.runtime.json_save_manager`: For schema validation of generated marks.
-   `engine.easter_eggs.contracts.survivor_mark.schema.json`: The schema defining the structure of survivor mark records.
-   `engine.save.schemas.floor_memory.schema.json`: The schema defining the structure of floor memory, which contains lists for easter eggs.
-   `engine.easter_eggs.registry.survivor_mark_registry.json`: Registry providing default values and definitions for mark and reward classes.