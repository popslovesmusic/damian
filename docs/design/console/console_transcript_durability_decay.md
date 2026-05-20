# Console Transcript Durability Decay Evidence

This document explains how the console transcript reporting system captures and records equipment durability decay during combat encounters.

## Overview

The `console_transcript_reporter` has been extended to capture the material deterioration of gear. By recording individual decay events and aggregate loss, the transcripts provide a material audit trail of how the player's equipment condition acts as a strategic strategic bottleneck.

## Captured Evidence

The transcript now includes the following durability decay observability fields:

*   **`durability_decay_observed`**: A boolean flag set to `True` if any equipment deterioration occurred during the session.
*   **`durability_events_observed`**: An integer count of individual items that lost durability.
*   **`total_durability_loss_observed`**: The cumulative amount of durability points lost across all equipped items in the session.
*   **`equipment_items_worn_observed`**: An array of unique equipment item IDs that suffered deterioration.
*   **`zero_durability_items_observed`**: A record of items that reached the **Zero-Floor Boundary** (0 durability) during combat.
*   **`durability_pressure_observed`**: A boolean flag indicating if significant gear strain was reported by the resolution stub.
*   **`durability_decay_summaries`**: An array of human-readable strings preserving the specific loss and remaining condition for every affected item.

## Integration Flow

1.  **Combat Resolution**: A `combat` command (e.g., `combat dangerous`) produces `durability_events` in its payload.
2.  **Payload Extraction**: The transcript reporter identifies the events and extracts item IDs, loss values, and final condition.
3.  **Aggregation**:
    *   `total_durability_loss_observed` is summed.
    *   Zero-durability reaches are flagged.
    *   Summaries are built from the material data.
4.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Consequence Preservation

The durability evidence system adheres to the core engine identity: **reward does not erase consequence**. 
- **Compounding Maintenance**: Wear is persistent across commands in the console, making the strategic management of repair materials (Stage 008) a material necessity for survival.
- **Zero-Floor Limit**: While items are not deleted at 0 durability (MVP rule), the transcript clearly marks them as broken, signaling a strategically locked or high-risk state.
- **Auditability**: Auditors can review exactly when and how an item was worn down, ensuring that gear-driven tradeoffs are balanced and deterministic.
