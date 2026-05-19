# Combat Transcript Loot and Resource Sink Evidence

This document explains how the console transcript reporting system captures and records loot events and resource sink pressure during combat encounters.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of the game's economy, specifically loot rewards and the associated resource costs (sinks). This ensures that wealth generation remains bounded and that the "Tower" remains difficult by reporting the estimated upkeep costs for the player.

## Captured Evidence

The transcript now includes the following loot and resource observability fields:

*   **`loot_events_observed`**: An integer count of how many combat sessions or events produced a bounded loot event.
*   **`total_gold_observed`**: The cumulative amount of gold granted across all observed loot events in the session.
*   **`large_visible_loot_observed`**: A boolean flag set to `True` if any single event granted 10,000 gold or more (typically a `VICTORY_ASCEND` outcome).
*   **`resource_sink_pressure_observed`**: A boolean flag indicating if resource sink pressure (estimated costs) was reported in the session.
*   **`bounded_reward_flags_clean`**: A critical safety boolean. It remains `True` only if no loot event granted power-bypassing abilities (e.g., invulnerability).
*   **`loot_sources_observed`**: An array of unique sources that produced loot (e.g., `combat_reward`).
*   **`resource_sink_summaries`**: An array of human-readable strings summarizing the estimated costs for potions, repairs, and mutation control for each encounter level.

## Integration Flow

1.  **Combat Execution**: A `combat` command is executed in the console.
2.  **Loot Generation**: The console produces a `loot_event` using the `mvp_loot_event_stub`.
3.  **Transcript Extraction**: The `console_transcript_reporter` inspects the `payload` of the combat result.
4.  **Evidence Aggregation**:
    *   Gold amounts are summed.
    *   Sink pressure is summarized into strings.
    *   Bounded reward flags are checked for safety violations.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Economic Observability

By capturing both the rewards (gold/materials) and the estimated costs (sinks), this system allows for a review of the game's "net economy" even before full inventory and shop systems are implemented. It ensures that wealth does not remove the inherent risks and consequences of the Tower.
