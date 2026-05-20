# Dashboard Domain Claim Evidence

This document explains how localized strategic footholds (Domain Claims) are integrated into the meta-strategic Domain Dashboard snapshots.

## Overview

The `domain_dashboard_snapshot_builder` has been updated to aggregate evidence of floor-level dominion. This ensures that when a player establishes a foothold in the Tower, its material impact on the "net economy"—including maintenance burden, visibility risk, and environmental mitigation—is reviewable in the dashboard.

## Integrated Evidence

The dashboard snapshot now includes a `domain_claim_summary` containing:

1.  **Claim Counts**: Separate tracking for **ACTIVE**, **DECAYING** (lacking upkeep), and **OVERRUN** (failed defense) claims.
2.  **Maintenance Pressure**: Surfaces the peak resource drain required to hold current territory. This represents the long-term operational burden of ownership.
3.  **Visibility Pressure**: Surfaces the peak "attention" the claims are attracting from the Tower's environmental hostility. High visibility increases the likelihood of claims becoming "scarred" by residue.
4.  **Mutation Threat**: Tracks the peak risk of environmental instability targeting the player's footholds.
5.  **Recovery Value**: The aggregate survival benefit (healing, supply relief) provided by all active claims.

## Strategic Cognition

By surfacing claim evidence in the dashboard, the "Tower" forces the player to weigh the meta-strategic benefits of territory against its compounding tactical costs. A player can now see if their network of "Recovery Anchors" is providing enough relief to justify the gold and shard drain of their collective maintenance pressure.

## Identity Preservation

*   **Evidence, not Safety**: Surfacing a claim's status in the dashboard does not make the claim itself safe. It only makes the *risk* to that claim legible.
*   **Hostility Preservation**: The dashboard tracks whether claims are correctly preserving the Tower's inherent hostility. If a claim were to somehow "bypass" tactical risk, this flag would alert auditors.
*   **Operational Uncertainty**: The dashboard derive information only from *known* claims and *current* state. It does not reveal "hidden" future events like impending mutation strikes or hidden room layouts.

## Integration Flow

1.  **Claim Creation**: The player uses the `claim` command to establish a foothold.
2.  **Snapshot Update**: The next `status` check or automated snapshot captures the new claim's operational profile.
3.  **Audit Recording**: The aggregated claim evidence is written to the dashboard snapshot and preserved in session transcripts for longitudinal review.
