# Console Transcript Traversal Evidence

This document explains how the console transcript reporting system captures and records spatial traversal evidence.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of the player's spatial choices and the associated material hazards. This ensures that the "journey" between floors—and the strategic risks incurred during movement—is materially recorded and reviewable.

## Captured Evidence

The transcript now includes the following traversal observability fields:

*   **`traversal_events_observed`**: An integer count of spatial movement attempts (`advance` or `escape`).
*   **`advance_attempts_observed`**: Specifically tracks attempts to move to the next floor.
*   **`escape_attempts_observed`**: Specifically tracks attempts to retreat back to the Hub.
*   **`traversal_pressure_observed`**: A boolean flag indicating if any traversal hazard evidence was captured.
*   **`traversal_pressure_values_observed`**: An array of aggregate burden values (0.0 to 1.0) encountered during movement or status checks.
*   **`highest_traversal_pressure_observed`**: Tracks the maximum movement hazard experienced in the session.
*   **`escape_risk_observed`**: A boolean flag indicating if escape risk was materially assessed.
*   **`escape_risk_values_observed`**: An array of risk values (0.0 to 1.0) associated with escape attempts.
*   **`highest_escape_risk_observed`**: Tracks the peak risk of failing a retreat.
*   **`route_exposure_values_observed`**: An array of the environmental exposure levels of the chosen paths.
*   **`traversal_summaries`**: An array of human-readable strings preserving the context and outcome of every spatial decision.

## Integration Flow

1.  **Traversal Command**: A spatial command (e.g., `advance` or `escape`) or a `status` check is executed.
2.  **Pressure Calculation**: The console uses `traversal_pressure_stub` to calculate current hazard and risk.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for the `traversal_event` and pressure metrics.
4.  **Aggregation**:
    *   Advance/Escape counts are incremented.
    *   Hazard and Risk values are added to their respective arrays.
    *   Maximum values are updated to track peak session pressure.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing spatial hazard, auditors can review the "journey" as a material strategically tradeoff. Transcripts reveal if a player is pushing their luck under high material burden or if they are retreating safely when risks become insurmountable. This reinforces the core principle that every decision in the Tower—including where you go—carries a physical and auditable consequence.
