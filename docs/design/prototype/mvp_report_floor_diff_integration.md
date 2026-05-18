# MVP End-to-End Report: Replay Floor Diff Integration

## Overview

This document details the integration of the Minimal Viable Prototype (MVP) Replay Floor Diff Reporter into the MVP End-to-End Scripted Run Report. The goal is to provide explicit evidence within the comprehensive report of how a floor's `floor_memory` changes after a `DEFEAT_DROP` outcome, demonstrating the successful application of residue, mutation, and survivor mark mechanics.

## Purpose

The primary objectives of this integration are:
1.  **Prove Mutation Impact**: Clearly show that the replay mutation process (triggered by `DEFEAT_DROP`) actually alters the floor's state as expected.
2.  **Verify Survivor Mark Attachment**: Confirm that new survivor marks are correctly attached to the mutated floor's memory.
3.  **Enhanced Observability**: Provide a summarized, human-readable view of these changes directly within the end-to-end report, making validation easier.
4.  **Complete MVP Picture**: Integrate all reactive core loop components into a single, verifiable report.

## Changes to MVP End-to-End Report

The `engine/reports/runtime/mvp_end_to_end_report.py` module has been updated:

-   **Capture Before/After States**: The report now logically identifies the specific floor that will undergo a replay mutation (e.g., floor 2 in the default sequence after a `DEFEAT_DROP`). It attempts to derive the "before" state (conceptually, the state of the floor before the `DEFEAT_DROP` step) and fetches the "after" state from the final `tower_state` saved by the simulation.
-   **Call Diff Reporter**: The `replay_floor_diff_reporter.make_replay_floor_diff_report()` function is called with these "before" and "after" `floor_memory` records.
-   **Include Diff Evidence**: The output of the diff reporter (including the readable summary and change details) is now embedded directly into the main end-to-end report.
-   **New Report Fields**: The `report_shape` has been extended to include:
    -   `replay_floor_diff_included`: Boolean, `True` if diff evidence was successfully generated.
    -   `replay_floor_diff_report_path`: String, path to the standalone diff report JSON file.
    -   `replay_floor_diff_summary`: Array of strings, the human-readable summary from the diff report.
    -   `replay_floor_changed`: Boolean, indicates if the floor's state visibly changed.
    -   `replay_floor_mutation_level_delta`: Integer, change in mutation level.
    -   `replay_floor_new_survivor_marks`: Integer, count of newly attached survivor marks.

## Behavior

-   The `run_mvp_end_to_end_report` executes the standard scripted sequence.
-   During processing, it identifies the floor that would be affected by a `DEFEAT_DROP` (floor 2 in the default sequence).
-   It uses the `replay_floor_diff_reporter` to compare the `floor_memory` of this specific floor before and after the simulated `DEFEAT_DROP` and mutation.
-   The generated diff report is saved as a separate JSON artifact within the overall report's output directory.
-   Key summary data from this diff report, along with its file path, is embedded into the main end-to-end report.
-   If the diff evidence generation fails for any reason (e.g., missing dependencies, invalid data), the main report's `ok` status might be affected, and structured errors will be recorded.

## Dependencies

-   `engine.reports.runtime.mvp_end_to_end_report`: The primary module being updated.
-   `engine.reports.runtime.replay_floor_diff_reporter`: Used to generate the floor diff evidence.
-   `engine.simulation.runtime.mvp_scripted_simulation`: Provides the simulation trace and final `tower_state`.
-   `engine.save.runtime.json_save_manager`: For loading the final `tower_state` and writing the diff report.

## Updated Structured End-to-End Report Shape

The `run_mvp_end_to_end_report` function's return structure now includes new fields:

```json
{
  "report_id": "string",
  "patch_id": "TOWER-ENGINE-033",
  "ok": "boolean",
  // ... (existing fields from TOWER-ENGINE-031) ...
  "replay_floor_diff_included": "boolean",          // NEW
  "replay_floor_diff_report_path": "string_or_null", // NEW
  "replay_floor_diff_summary": "array",             // NEW
  "replay_floor_changed": "boolean",                // NEW
  "replay_floor_mutation_level_delta": "integer",   // NEW
  "replay_floor_new_survivor_marks": "integer",     // NEW
  "no_scope_creep_flags": "object",
  "errors": "array"
}
```