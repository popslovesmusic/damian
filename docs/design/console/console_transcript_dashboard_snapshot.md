# Console Transcript Dashboard Snapshot Evidence

This document explains how the console transcript reporting system captures and records meta-strategic domain dashboard snapshots.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of the Tower's meta-strategic state. This ensures that the aggregated survival pressure, operational burden, and recursive history—surfaced through the **Domain Dashboard**—are materially recorded and reviewable in session transcripts.

## Captured Evidence

The transcript now includes the following dashboard observability fields:

*   **`dashboard_snapshots_observed`**: An integer count of all meta-strategic snapshots generated during the session.
*   **`dashboard_status_observed`**: A boolean flag indicating if at least one dashboard report was materially generated.
*   **`pressure_summaries_observed`**: An array of the weighted hazard profiles (Combat, Traversal, Escape, Mutation, Repair, Capacity) captured from each snapshot.
*   **`resource_summaries_observed`**: An array of visible inventory supplies (Gold, Potions, Rare Materials).
*   **`equipment_summaries_observed`**: An array of gear condition reports (Damaged Items, Zero-Durability Items).
*   **`route_summaries_observed`**: An array of topological movement histories.
*   **`residue_summaries_observed`**: An array of recursive history records (Triggered Mutations, Survivor Marks).
*   **`recoverability_statuses_observed`**: An array of survival cognition assessments (Recoverability, Critical Pressure).
*   **`dashboard_survival_summaries`**: An array of human-readable strategic summaries preserving the "net economy" of the session.

## Integration Flow

1.  **Status Command**: The player executes the `status` command.
2.  **Snapshot Generation**: The console calls `domain_dashboard_snapshot_builder.build_domain_dashboard_snapshot`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for the `dashboard_snapshot` record and summary.
4.  **Aggregation**:
    *   Snapshot counts are incremented.
    *   Detailed summaries (Pressure, Resource, Equipment, etc.) are added to their respective arrays for longitudinal analysis.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing meta-strategic snapshots, auditors can review the "compounding health" of a run. Transcripts reveal not just individual tactical outcomes, but how those outcomes are aggregating into total operational hazard. This reinforces the core principle that every decision in the Tower—from combat to inventory management—contributes to a physical, auditable, and meta-strategic survival burden.
