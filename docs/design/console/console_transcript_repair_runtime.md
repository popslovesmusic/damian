# Console Transcript Repair Runtime Evidence

This document explains how the console transcript reporting system captures and records equipment repair runtime evidence.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of the material maintenance cycle. This ensures that when a player repairs their gear by consuming resources, the resulting durability restoration and material cost are materially recorded and reviewable.

## Captured Evidence

The transcript now includes the following repair runtime observability fields:

*   **`repair_events_observed`**: An integer count of attempted `repair` command executions.
*   **`repair_applications_observed`**: The count of successfully applied durability restorations.
*   **`repair_failures_observed`**: A count of attempted repairs that failed safely (e.g., due to insufficient materials).
*   **`total_durability_restored_observed`**: The cumulative amount of durability points restored across all items in the session.
*   **`repair_materials_consumed_observed`**: The total quantity of `repair_material_basic` consumed through successful repairs.
*   **`equipment_items_repaired_observed`**: An array of unique equipment item IDs that underwent material restoration.
*   **`bounded_repair_clean`**: A safety boolean confirming that no repair event exceeded the maximum durability of an item or violated anti-inflationary rules.
*   **`repair_runtime_summaries`**: An array of human-readable strings preserving the results and failure reasons for every attempted repair.

## Integration Flow

1.  **Repair Command**: A console command (e.g., `repair 2`) is executed.
2.  **Runtime Execution**: The console calls `repair_runtime_stub.apply_repair`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for the `repair_event` and `inventory_transaction`.
4.  **Aggregation**:
    *   Durability restored is added to `total_durability_restored_observed`.
    *   Material costs are added to `repair_materials_consumed_observed`.
    *   Safety checks are performed to set `bounded_repair_clean`.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing material restoration, auditors can review the "maintenance loop" of the Tower. Transcripts reveal if a player is successfully converting their looted materials into operational longevity, or if they are operating under the stress of broken gear because they lack the resources to maintain it. This reinforces the core principle that gear condition is a material estratégico bottleneck.
