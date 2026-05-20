# Console Transcript Capacity Pressure Evidence

This document explains how the console transcript reporting system captures and records material inventory capacity pressure.

## Overview

The `console_transcript_reporter` has been extended to capture the cumulative strategic burden of held items. By recording capacity pressure and strategic bands, the transcripts provide an audit trail of the player's material strategic flexibility and the consequences of their resource management choices.

## Captured Evidence

The transcript now includes the following capacity pressure observability fields:

*   **`capacity_pressure_observed`**: A boolean flag set to `True` if any valid capacity pressure payload was encountered.
*   **`capacity_pressure_values_observed`**: An array of bounded pressure values (0.0 to 1.0) captured throughout the session.
*   **`capacity_bands_observed`**: A unique array of strategic bands (EMPTY, LOW, MODERATE, HIGH, FULL) encountered.
*   **`highest_capacity_pressure_observed`**: The maximum capacity pressure value recorded during the session.
*   **`over_capacity_failures_observed`**: A count of attempted material additions that failed due to the bag being full.
*   **`material_burden_summaries`**: An array of human-readable strings summarizing the bag burden (used/total and band) after material transactions.

## Integration Flow

1.  **Console Interaction**: A console command (e.g., `status`, `combat`, `potion`) returns a `capacity_pressure_summary` in its payload.
2.  **Payload Extraction**: The transcript reporter identifies the summary and extracts the pressure value, band, and overflow status.
3.  **Aggregation**:
    *   The `highest_capacity_pressure_observed` is updated.
    *   Bands and values are appended to their respective evidence arrays.
    *   Overflows increment `over_capacity_failures_observed`.
4.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing material burden, auditors can review the "Tower" as a series of strategic strategic tradeoffs. Transcripts now reveal if a player achieved victory while operating under the stress of a **HIGH** or **FULL** bag, or if they were forced into a safe failure due to poor supply management.
