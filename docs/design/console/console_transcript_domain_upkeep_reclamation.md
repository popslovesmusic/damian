# Console Transcript Domain Upkeep and Reclamation

This document explains how the console transcript reporting system captures the active struggle between established Order and Tower Reclamation.

## Overview

The `console_transcript_reporter` has been extended to record the longitudinal health of territory management. This ensures that the material cost of upkeep, the consequences of decay, and the escalating response of the Tower are materially captured and reviewable in session transcripts.

## Captured Evidence

The transcript now includes the following upkeep and reclamation observability fields:

### Domain Upkeep
*   **`upkeep_events_observed`**: Count of manual maintenance operations performed.
*   **`total_shards_consumed_observed`**: Aggregate material cost of maintaining order during the session.
*   **`foothold_decay_events_observed`**: Count of instances where established order degraded due to lack of upkeep.
*   **`foothold_restoration_events_observed`**: Count of instances where order was restored from a decayed state.
*   **`upkeep_summaries`**: Human-readable records of shard expenditures and state outcomes.

### Tower Reclamation
*   **`reclamation_pressure_observed`**: Boolean indicating if the Tower's environmental pushback was detected.
*   **`reclamation_pressure_values_observed`**: Longitudinal record of aggregate environmental irritation (0.0 to 1.0).
*   **`highest_reclamation_pressure_observed`**: The peak counter-force recorded during the run.
*   **`reclamation_bands_observed`**: The specific threat levels (STABLE to CRITICAL) encountered.
*   **`reclamation_summaries`**: Descriptive records of the contributions (visibility, decay, depth) to reclamation drive.

## Integration Flow

1.  **Maintenance Loop**: The player executes `maintain` or `status` commands.
2.  **Evidence Extraction**: The transcript reporter inspects the command payloads for `upkeep_events` and `reclamation_pressure` records.
3.  **Aggregation**: Data is summed, peaked, and recorded to provide a timeline of the "conquest health."
4.  **Audit Trail**: The results are preserved in the JSON transcript for post-run analysis.

## Strategic Observability

By capturing this evidence, transcripts reveal the true cost of territorial ambition. Auditors can analyze whether the player's shard economy is sustainable or if their established footholds are generating more environmental irritation than they are worth in strategic relief. This reinforces the core principle that every foothold established is a target created, and every shard spent is a material tradeoff in the strategic journey.
