# Console Transcript Domain Claim Evidence

This document explains how the console transcript reporting system captures and records evidence of establishing localized strategic footholds (Domain Claims).

## Overview

The `console_transcript_reporter` has been extended to capture the creation and operational impact of domain footholds. This ensures that the player's transition from tactical survival to meta-strategic territory management is materially recorded and reviewable in session transcripts.

## Captured Evidence

The transcript now includes the following domain claim observability fields:

*   **`domain_claims_observed`**: An integer count of all localized footholds established during the session.
*   **`domain_claim_types_observed`**: An array of the unique claim types (e.g., `recovery_anchor`, `repair_station`) established.
*   **`highest_domain_maintenance_pressure_observed`**: The peak operational burden recorded among all claims. This scales with floor depth and established complexity.
*   **`highest_domain_visibility_pressure_observed`**: The peak "attention" attracted from the Tower's environmental hostility.
*   **`highest_domain_mutation_threat_observed`**: The peak risk of claims becoming "scarred" by residue.
*   **`total_domain_recovery_value_observed`**: The aggregate strategic benefit provided by all claims established during the run.
*   **`tower_hostility_preserved_observed`**: A boolean flag ensuring that claims are not bypassing the Tower's inherent strategic hostility.
*   **`domain_claim_summaries`**: An array of human-readable summaries for each foothold established.

## Integration Flow

1.  **Claim Command**: The player executes the `claim` command (e.g., `claim supply_cache`).
2.  **Foothold Creation**: The console calls `domain_claim_stub.make_domain_claim`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for the `domain_claim` record and summary.
4.  **Aggregation**:
    *   Claim counts are incremented.
    *   Pressures and recovery values are tracked and accumulated.
    *   Hostility preservation is verified.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing domain claim evidence, transcripts provide a clear audit trail of how players are establishing and maintaining order within the Tower. Auditors can review whether the strategic benefits of a foothold (Recovery Value) justify its long-term operational costs (Maintenance Pressure) and environmental risks (Visibility Pressure). This reinforces the core principle that owning territory is a material strategic task, not a safety valve.
