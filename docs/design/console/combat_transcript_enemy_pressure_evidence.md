# Combat Transcript Enemy Pressure Evidence

This document explains how the console transcript reporting system captures and records enemy pressure evidence during combat encounters.

## Overview

The `console_transcript_reporter` has been extended to capture detailed evidence of the tower's adaptive enemy selection. This allows for post-session auditing of how the tower is responding to player actions and floor states.

## Captured Evidence

The transcript now includes the following observability fields:

*   **`enemy_pressure_profiles_observed`**: An integer count of how many combat sessions utilized an adaptive enemy pressure profile.
*   **`enemy_archetypes_observed`**: An array of unique enemy archetype IDs (e.g., `attrition_unit`, `counter_unit`) encountered during the session.
*   **`enemy_adaptation_reasoning_observed`**: An aggregate array of unique reasoning strings provided by the `enemy_pressure_selector`. This explains *why* the tower chose specific adaptations.
*   **Pressure Category Flags**: Boolean flags that indicate if specific types of pressure were manifested:
    *   `attrition_pressure_observed`: True if an `attrition_unit` was encountered.
    *   `counter_pressure_observed`: True if a `counter_unit` was encountered.
    *   `ambush_pressure_observed`: True if an `ambush_unit` was encountered.
    *   `baseline_pressure_observed`: True if a `pressure_unit` (standard) was encountered.

## Integration Flow

1.  **Combat Execution**: During a console session, the `combat` command is executed.
2.  **Payload Inspection**: The `console_transcript_reporter` inspects the `payload` of the `combat` command result.
3.  **Evidence Extraction**: If `enemy_pressure_profile_used` is true, the reporter extracts the `enemy_archetype_id` and `enemy_adaptation_reasoning`.
4.  **Aggregation**: The extracted data is aggregated into the session-level transcript object.
5.  **Audit Recording**: The final transcript is written to `outputs/console_transcripts/`, providing a permanent record of the tower's adaptive behavior.

## Observability Benefits

This evidence capture ensures that the "Tower" remains observable and accountable to its design principles (e.g., bounded difficulty, deterministic adaptation). Auditors can review transcripts to verify that the tower is not manifesting unfair combinations of pressure or bypassing the outcome pipeline.
