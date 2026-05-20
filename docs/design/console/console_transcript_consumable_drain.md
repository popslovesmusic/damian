# Console Transcript Consumable Drain Evidence

This document explains how the console transcript reporting system captures and records material consumable usage (specifically potions) and resource drain.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of material resource consumption. This ensures that when a player uses potions to manage health or respond to combat pressure, the resulting inventory deduction and drain are materially recorded and reviewable.

## Captured Evidence

The transcript now includes the following consumable drain observability fields:

*   **`consumable_uses_observed`**: An integer count of successful `potion` command executions.
*   **`consumables_deducted_observed`**: The total quantity of items removed from inventory through consumable usage.
*   **`failed_consumable_attempts_observed`**: A count of attempted potion uses that failed safely (e.g., due to insufficient inventory).
*   **`potion_drain_observed`**: A boolean flag indicating if any successful material potion drain occurred during the session.
*   **`total_potions_consumed`**: An aggregate count of all potions materially consumed.
*   **`consumable_drain_summaries`**: An array of human-readable strings preserving the results and failure reasons for every attempted consumable use.

## Integration Flow

1.  **Consumable Command**: A console command (e.g., `potion 2`) is executed.
2.  **Inventory Transaction**: The console calls `inventory_transaction_stub.consume_inventory_item`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for `consumable_used` and the associated `inventory_transaction`.
4.  **Aggregation**:
    *   Successful uses increment `consumable_uses_observed`.
    *   Quantities are added to `total_potions_consumed`.
    *   Summaries are recorded for both success and safe-failure states.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

Capturing material drain ensures that the "Tower" remains a series of strategic tradeoffs. If a combat transcript reports high pressure, the auditor can verify if the player actually possessed and consumed the necessary resources to survive, or if the "net economy" is becoming unbalanced.
