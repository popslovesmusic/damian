# Console Transcript Repair Material Drain Evidence

This document explains how the console transcript reporting system captures and records material repair material deductions and repair pressure.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of material equipment maintenance. This ensures that when a player deducts repair materials to respond to equipment pressure, the resulting inventory change is materially recorded and reviewable.

## Captured Evidence

The transcript now includes the following repair material drain observability fields:

*   **`repair_material_uses_observed`**: An integer count of successful `repair` command executions.
*   **`repair_materials_deducted_observed`**: The total quantity of repair materials removed from inventory.
*   **`failed_repair_attempts_observed`**: A count of attempted repair material uses that failed safely (e.g., due to insufficient inventory).
*   **`repair_material_drain_observed`**: A boolean flag indicating if any successful material repair drain occurred during the session.
*   **`durability_restoration_observed`**: A critical boundary boolean. For the current stage, this remains **`false`**, as the `repair` command only tests economic drain and does not yet restore equipment durability.
*   **`repair_drain_summaries`**: An array of human-readable strings preserving the results and failure reasons for every attempted repair material use.

## Integration Flow

1.  **Repair Command**: A console command (e.g., `repair 1`) is executed.
2.  **Inventory Transaction**: The console calls `inventory_transaction_stub.consume_inventory_item` for `repair_material_basic`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for `repair_material_deducted` and the associated `inventory_transaction`.
4.  **Aggregation**:
    *   Successful uses increment `repair_material_uses_observed`.
    *   Quantities are added to `repair_materials_deducted_observed`.
    *   Summaries are recorded for both success and safe-failure states.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

Capturing material repair drain ensures that equipment upkeep is a tangible estratégico bottleneck. By reviewing transcripts, auditors can verify if the player is maintaining a sustainable surplus of repair materials or if they are operating under high equipment pressure without the material means to address it.
