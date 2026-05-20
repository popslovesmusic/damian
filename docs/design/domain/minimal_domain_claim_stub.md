# Minimal Domain Claim Stub

This document explains the deterministic domain claim stub implementation for the Tower Engine MVP.

## Overview

The `domain_claim_stub` provides the first mechanical framework for establishing localized footholds within the Tower's topography. It allows players to "claim" specific room nodes, turning them into strategic assets with unique operational properties.

## Claim Types and Behavior

To ensure a balanced spatial economy, claims are classified into several types, each with a unique strategic bias:

1.  **Recovery Anchor**: Optimized for survival recovery. High recovery value with minimal maintenance burden.
2.  **Supply Cache**: A localized resource hub. Moderate visibility pressure but supports inventory relief.
3.  **Repair Station**: Focused on gear maintenance. Higher maintenance pressure but materially improves repair efficiency.
4.  **Survivor Outpost**: A high-visibility foothold. Significant visibility and maintenance pressure, but provides the highest recovery and strategic support.
5.  **Observation Post**: Low maintenance foothold used for tracking environmental stability and route hazards.

## Calculation Rules (Material Strategic Hazard)

To maintain engine integrity, claim hazards are calculated using the following rules:

*   **Maintenance Pressure**: Represents the constant resource drain needed to hold the node. This scales with floor depth, ensuring that deep footholds are materially more expensive to maintain.
*   **Visibility Pressure**: Represents how much the claim attracts the Tower's environmental hostility (residue). Higher visibility increases the likelihood of the claim being targeted by mutations.
*   **Recovery Value**: The material strategic benefit the claim provides to the player (e.g., healing or resource generation).
*   **Mutation Threat**: The specific risk of the claim being "scarred" by environmental instability, scaling with local residue strength.

## Bounded Results

All individual and aggregate metrics are strictly bounded between `0.0` (safe/low cost) and `1.0` (critical hazard/high cost). Claims are designed to **materialize burden**, meaning that owning territory is not an instant safety valve but a strategic task requiring future upkeep and defense.

## Non-Base-Building Boundary

This stub is strictly responsible for **calculating and validating claim state**. It does not handle:
*   Visual base building or voxel editing.
*   Rendered housing interiors or furniture.
*   Real-time territory wars or combat defense.
*   Animation of construction.
