# MVP Outcome Pipeline

## Overview

This document describes the Minimal Viable Prototype (MVP) Outcome Pipeline, a core component responsible for processing the results of a player's interaction with a floor. It integrates several existing MVP modules to handle progression changes, residue recording, floor mutations, and (optionally) the attachment of survivor marks based on the outcome.

## Purpose

The primary objective of this pipeline is to provide a unified mechanism for:
1.  Applying player and tower progression rules based on a given outcome (e.g., victory, defeat).
2.  Recording structured residue data for analysis and future mutations.
3.  Triggering replay-floor mutations under specific conditions (e.g., defeat).
4.  Attaching optional hidden survivor marks to mutated floors, enhancing replayability and discoverability.

This pipeline ensures that the game's core loop, from player action to systemic reaction, is consistently applied and traceable.

## Key Functions

-   **`resolve_mvp_floor_outcome(tower_state, outcome, debug=False)`**:
    The main entry point for the pipeline. It takes the current `tower_state` and a defined `outcome` (e.g., "VICTORY_ASCEND", "DEFEAT_DROP", "RETREAT_TO_HUB", "EXIT_GAME") and orchestrates the subsequent steps.
-   **`resolve_victory_pipeline(tower_state, debug=False)`**:
    Handles the "VICTORY_ASCEND" outcome. It applies positive progression (e.g., ascending a floor), writes residue related to the victory, and explicitly *does not* trigger floor mutations or attach survivor marks in this MVP.
-   **`resolve_defeat_drop_pipeline(tower_state, debug=False)`**:
    Handles the "DEFEAT_DROP" outcome. This is the most complex path in the MVP. It applies negative progression (e.g., dropping a floor), writes residue for the defeat, applies a replay-floor mutation stub to the newly returned floor, and attaches a new, optional survivor mark to that mutated floor's memory.
-   **`validate_pipeline_result(result, debug=False)`**:
    Ensures that the output of any pipeline execution adheres to the expected structured result shape.

## Pipeline Behavior

-   **VICTORY_ASCEND**:
    -   Records the previous floor.
    -   Applies progression: ascends player to the next floor.
    -   Writes "VICTORY_ASCEND" residue to the *previous* floor.
    -   Does not apply a mutation stub.
    -   Does not attach a survivor mark.
-   **DEFEAT_DROP**:
    -   Records the previous floor.
    -   Applies progression: drops player to a lower floor.
    -   Writes "DEFEAT_DROP" residue to the *returned current* floor.
    -   Applies the replay-floor mutation stub to the *returned current* floor.
    -   Creates and attaches an optional hidden survivor mark to the *returned current* floor's memory.
-   **RETREAT_TO_HUB**:
    -   Applies progression: returns player to hub (current floor remains unchanged in MVP context).
    -   Writes "RETREAT_TO_HUB" residue to the *current* floor.
    -   Does not apply a mutation stub.
    -   Does not attach a survivor mark.
-   **EXIT_GAME**:
    -   Applies progression: exits the game (current floor remains unchanged in MVP context).
    -   Writes "EXIT_GAME" residue to the *current* floor.
    -   Does not apply a mutation stub.
    -   Does not attach a survivor mark.

## Dependencies

-   `engine.debug.runtime.debug_logger`: For structured debug logging.
-   `engine.progression.runtime.mvp_floor_progression`: For applying floor-based progression rules.
-   `engine.residue.runtime.mvp_residue_writer`: For writing residue records.
-   `engine.mutation.runtime.mvp_floor_mutation_stub`: For applying simulated floor mutations.
-   `engine.easter_eggs.runtime.mvp_survivor_mark_system`: For creating and attaching survivor marks.

## Structured Result Shape

The `resolve_mvp_floor_outcome` function returns a dictionary with the following structure:

```json
{
  "ok": "boolean",
  "outcome": "string",
  "previous_floor": "integer_or_null",
  "current_floor": "integer_or_null",
  "tower_state": "object_or_null",
  "progression_result": "object_or_null",
  "residue_result": "object_or_null",
  "mutation_result": "object_or_null",
  "mutation_applied": "boolean",
  "survivor_mark_result": "object_or_null",
  "survivor_mark_attached": "boolean",
  "error": "object_or_null"
}
```

This ensures that the pipeline's output is consistent, allowing for easy integration with downstream systems (like the simulation harness or reporting).