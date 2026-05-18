# MVP Scripted Simulation Harness

## Overview

This document describes the Minimal Viable Prototype (MVP) Scripted Simulation Harness. This component provides a deterministic environment to execute predefined sequences of floor outcomes through the MVP outcome pipeline. Its primary purpose is to test the end-to-end flow of progression, residue writing, mutation application, and survivor mark attachment, as well as the persistence of the game state between steps.

## Purpose

The main objectives of the simulation harness are:
1.  **Deterministic Testing**: Allow for repeatable execution of specific gameplay scenarios to verify the correctness and consistency of the MVP engine components.
2.  **Integration Validation**: Confirm that the `mvp_outcome_pipeline`, bootstrappers, and save runtime interact correctly to maintain a coherent game state.
3.  **Mutation Persistence Proof**: Specifically validate that any replay-floor mutations applied are correctly stored in the `tower_state` and can be retrieved.
4.  **Artifact Generation**: Produce structured results that can be analyzed and included in broader reports (e.g., the end-to-end report).

## Key Functions

-   **`run_scripted_simulation(sequence, save_dir='saves/simulations', debug=False)`**:
    The main function to execute a given list of outcomes (`sequence`). It bootstraps the initial game state, iterates through the outcomes, calls the `mvp_outcome_pipeline` for each step, and persists the final game state.
-   **`make_scripted_sequence(name='default_sequence')`**:
    Generates predefined sequences of outcomes. The `default_sequence` covers a basic flow including victories, a defeat, and an exit.
-   **`load_simulation_results(path)`**:
    Loads a previously saved simulation result artifact from a specified path.
-   **`summarize_simulation_result(result)`**:
    Provides a concise, human-readable summary of a completed simulation run.

## Default Scripted Sequence

The `default_sequence` is designed to exercise key aspects of the pipeline:

```
[
  "VICTORY_ASCEND",       // Ascends, writes residue
  "VICTORY_ASCEND",       // Ascends further, writes residue
  "DEFEAT_DROP",          // Drops a floor, writes residue, applies mutation, attaches survivor mark
  "VICTORY_ASCEND",       // Ascends again, writes residue
  "EXIT_GAME"             // Writes residue, exits
]
```

## Expected Behavior

-   The simulation starts by bootstrapping valid `tower_state`, `player_progression`, and `domain_state`.
-   Each outcome in the `sequence` is executed in order using the `mvp_outcome_pipeline`.
-   The `tower_state` correctly persists and updates between steps.
-   `DEFEAT_DROP` outcomes trigger the replay-floor mutation stub and attach a survivor mark to the affected floor's memory.
-   Mutations and attached survivor marks are verifiable in the saved `tower_state`.
-   A structured simulation result artifact is written to `outputs/simulations/`.

## Dependencies

-   `engine.debug.runtime.debug_logger`: For structured debug logging.
-   `engine.prototype.runtime.mvp_outcome_pipeline`: For processing individual floor outcomes.
-   `engine.save.bootstrap.tower_state_bootstrapper`: For initializing and saving `tower_state`.
-   `engine.player.bootstrap.player_progression_bootstrapper`: For initializing `player_progression`.
-   `engine.domain.bootstrap.domain_state_bootstrapper`: For initializing `domain_state`.
-   `engine.save.runtime.json_save_manager`: For loading/saving JSON artifacts.

## Structured Simulation Result Shape

The `run_scripted_simulation` function returns a dictionary with the following structure:

```json
{
  "ok": "boolean",
  "sequence_name": "string",
  "steps_executed": "integer",
  "final_floor": "integer",
  "highest_floor_reached": "integer",
  "mutation_events_triggered": "integer",
  "residue_records_written": "integer",
  "final_tower_state_path": "string",
  "errors": "array"
}
```