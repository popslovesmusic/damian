# Minimal Claim Targeting Stub

This document explains the deterministic implementation of Claim Targeting for the Tower Engine MVP.

## Overview

The `claim_targeting_stub` calculates the focused environmental pressure exerted by the Tower against a specific strategic foothold. It turns territorial control into a dynamic struggle by measuring how "audible" and "vulnerable" a claim is to focused reclamation attempts.

## Calculation Factors

Targeting pressure (0.0 to 1.0) is derived from the following factors:

1.  **Visibility Signal**: The primary driver. High-visibility footholds (like Outposts) attract more focused attention.
2.  **Order Fragility (Local Scarring)**: Nodes with high environmental degradation are "unstable ground," making the claims on them easier for the Tower to target.
3.  **Floor-Wide Reclamation Drive**: The general hostility of the floor acts as a multiplier, escalating focused targeting when the entire environment isIrritated.

## Strategic Impact (Upkeep Penalty)

Targeting is not just a passive metric; it has a material impact on territory management:

*   **Maintenance Penalty**: Heavily targeted claims are more difficult to hold. This is materially represented by an increase in their per-run Stability Shard cost.
*   **Destabilization**: Critical targeting levels ( > 0.7) trigger destabilization events. Destabilized footholds provide reduced strategic support and are at immediate risk of becoming **OVERRUN**.

## Bounded Results

All targeting metrics are strictly bounded between `0.0` and `1.0`. The stub ensures that while environmental pushback increases operational burden, it does not instantly erase player progress, allowing for a "pressure and response" strategic loop.

## Non-Spatial Boundary

This stub is strictly responsible for **calculating and reporting focused environmental irritation**. It does not handle:
*   Physical enemy sieges or base defense combat.
*   Rendered structural damage animations.
*   Instant deletion of claims without preceding decay states.
