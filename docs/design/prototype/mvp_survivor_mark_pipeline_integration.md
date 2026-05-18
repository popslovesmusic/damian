# MVP Survivor Mark Pipeline Integration

## Overview

This document details the integration of the Minimal Viable Prototype (MVP) Survivor Mark System into the MVP Outcome Pipeline. Specifically, it focuses on how hidden survivor marks are optionally created and attached to floor memory when a `DEFEAT_DROP` outcome triggers a replay-floor mutation. This integration ensures that the consequences of certain player actions (defeats) can lead to new, discoverable content.

## Purpose

The primary objectives of this integration are:
1.  **Enhance Replayability**: Provide a mechanism for replay-mutated floors to offer unique content, encouraging re-exploration.
2.  **Connect Systems**: Demonstrate a tangible link between the progression, residue, mutation, and easter egg systems.
3.  **Visible Consequences**: Make the effects of a `DEFEAT_DROP` more impactful and observable, beyond just a floor change.
4.  **Preserve Rules**: Ensure that survivor marks, even when integrated, adhere to their core rules (optional, discoverable, bounded rewards).

## Changes to MVP Outcome Pipeline

The `engine/prototype/runtime/mvp_outcome_pipeline.py` module has been updated:

-   **`resolve_defeat_drop_pipeline(tower_state, debug=False)`**:
    -   After applying progression (dropping a floor) and applying the replay-floor mutation stub, this function now calls `mvp_survivor_mark_system.make_survivor_mark()` to create a new mark.
    -   The newly created mark is then attached to the `floor_memory` of the returned current floor using `mvp_survivor_mark_system.attach_survivor_mark_to_floor_memory()`.
    -   The pipeline's result now includes `survivor_mark_result` (the created mark object) and `survivor_mark_attached` (a boolean flag set to `True`).

-   **`resolve_mvp_floor_outcome(tower_state, outcome, debug=False)`**:
    -   The result structure now consistently includes `survivor_mark_result` (set to `None` for non-DEFEAT_DROP outcomes) and `survivor_mark_attached` (set to `False` for non-DEFEAT_DROP outcomes).

## Pipeline Behavior (DEFEAT_DROP after Integration)

-   Records the previous floor.
-   Applies progression: drops player to a lower floor.
-   Writes "DEFEAT_DROP" residue to the *returned current* floor.
-   Applies the replay-floor mutation stub to the *returned current* floor.
-   **Creates a survivor mark for the *returned current* floor.**
-   **Attaches the new survivor mark to the *returned current* floor's memory (`unclaimed_easter_eggs`).**
-   The pipeline result indicates `survivor_mark_attached = True` and includes the `survivor_mark_result`.

## Non-Defeat Outcomes

For outcomes such as `VICTORY_ASCEND`, `RETREAT_TO_HUB`, and `EXIT_GAME`, the pipeline's behavior regarding survivor marks remains unchanged: no new survivor marks are created or attached. The result will consistently show `survivor_mark_attached = False` and `survivor_mark_result = None`.

## Dependencies

-   `engine.prototype.runtime.mvp_outcome_pipeline`: The primary module being updated.
-   `engine.easter_eggs.runtime.mvp_survivor_mark_system`: Used for creating and attaching marks.
-   `engine.residue.runtime.mvp_residue_writer`: Used to get/create floor memory to attach the mark to.

## Updated Structured Result Shape

The `resolve_mvp_floor_outcome` function's return structure now includes new fields:

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
  "survivor_mark_result": "object_or_null",    // NEW: The created survivor mark object
  "survivor_mark_attached": "boolean",          // NEW: True if a mark was attached
  "error": "object_or_null"
}
```