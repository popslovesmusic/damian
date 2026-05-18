# MVP Text Console Replay Floor Diff Reporter

## Overview

This document describes the Minimal Viable Prototype (MVP) Text Console Replay Floor Diff Reporter. This utility provides a non-graphical way to observe the changes that occur to a floor's `floor_memory` (its persistent state) after a replay mutation has been applied. It's crucial for verifying the impact of mutation without needing a full rendering or map generation system.

## Purpose

The primary objectives of this reporter are:
1.  **Observability**: Provide clear, structured evidence of how a floor's state changes due to residue and mutation.
2.  **Verification**: Allow for auditing that replay mutations are indeed altering floor characteristics as expected, and that survivor marks are correctly attached.
3.  **Debuggability**: Aid in understanding the dynamic behavior of floors within the text console environment.
4.  **System Independence**: Operate without reliance on rendering or map generation components, focusing purely on state changes.

## Key Functions

-   **`snapshot_floor_memory(floor_memory)`**:
    Creates a simplified, standardized snapshot of a `floor_memory` record. This snapshot includes key immutable and mutable attributes relevant for comparison (e.g., `mutation_level`, `active_mutations`, `unclaimed_easter_eggs`).
-   **`diff_floor_snapshots(before_snapshot, after_snapshot, debug=False)`**:
    Compares two `floor_memory` snapshots for the same `floor_id`. It calculates deltas for numerical values and identifies new elements in lists (like active mutations or survivor marks). Returns a `changed` boolean and a `diff` dictionary.
-   **`make_replay_floor_diff_report(before_floor_memory, after_floor_memory, debug=False)`**:
    The main report generation function. It takes two `floor_memory` records (before and after mutation), creates snapshots, calculates the diff, and compiles a comprehensive report, including a human-readable summary.
-   **`write_replay_floor_diff_report(report, output_path)`**:
    Writes the generated diff report to a JSON file at the specified `output_path`.
-   **`summarize_replay_floor_diff(diff_data)`**:
    Generates an array of human-readable strings summarizing the key changes found in the `diff_data`, explicitly covering mutation level changes, new active mutations, new survivor marks, and residue history changes.

## Snapshot Shape

A snapshot is a simplified dictionary derived from `floor_memory`:

```json
{
  "floor_id": "integer",
  "visit_count": "integer",
  "death_count": "integer",
  "victory_count": "integer",
  "stability": "number",
  "deviation": "number",
  "mutation_level": "integer",
  "known_layout_seed": "string",
  "active_mutations": "array",
  "discovered_easter_eggs": "array",
  "unclaimed_easter_eggs": "array",
  "residue_history_count": "integer"
}
```

## Diff Report Shape

The `make_replay_floor_diff_report` function returns a dictionary with the following structure:

```json
{
  "report_id": "string",
  "ok": "boolean",
  "floor_id": "integer_or_null",
  "changed": "boolean",
  "before": "object_or_null",
  "after": "object_or_null",
  "changes": {
    "mutation_level_delta": "integer",
    "stability_delta": "number",
    "deviation_delta": "number",
    "new_active_mutations": "array",
    "new_unclaimed_survivor_marks": "array",
    "new_discovered_survivor_marks": "array",
    "residue_history_delta": "integer"
  },
  "readable_summary": "array",
  "error": "object_or_null"
}
```

## Readable Summary Requirements

The `readable_summary` must clearly articulate:
-   A statement confirming floor identity appears preserved (conceptual for MVP).
-   Any change in `mutation_level`.
-   Any newly `active_mutations`.
-   Any newly `unclaimed_easter_eggs` or `discovered_easter_eggs`.
-   Any change in `residue_history_count`.

## Dependencies

-   `engine.debug.runtime.debug_logger`: For structured debug logging.
-   `engine.save.runtime.json_save_manager`: For writing the JSON report artifact.
-   `engine.save.schemas.floor_memory.schema.json`: For understanding the structure of floor memory.