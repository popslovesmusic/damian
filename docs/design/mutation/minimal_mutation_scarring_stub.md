# Minimal Mutation Scarring Stub

This document explains the deterministic implementation of Mutation Scarring for the Tower Engine MVP.

## Overview

The `mutation_scarring_stub` calculates the environmental degradation caused by established Order (footholds). It materializes the principle that "Order leaves a mark" by measuring the localized stress a foothold exerts on its room node.

## Calculation Rules

Scarring intensity is derived from the following factors:

1.  **Baseline Stress**: Any localized order creates a minimum environmental stain (0.1).
2.  **Visibility Pressure**: The more "audible" a foothold is to the Tower, the faster it scars its node.
3.  **Foothold Decay**: Neglected footholds (`DECAYING` or `OVERRUN`) create localized instability, significantly increasing scar intensity.
4.  **Tower Depth**: Deeper floors are more reactive, increasing baseline scarring rates.

## Hazard Bias (Material Impact)

Scarring is not just a cosmetic metric. It generates a **Hazard Bias**, which is a material increase in the tactical difficulty and mutation probability of the node. This ensures that:
*   Owned nodes become progressively more dangerous over time.
*   Failed footholds leave behind "hostile zones" that must be stabilized or avoided.
*   Dominion carries a physical, auditable environmental cost.

## Bounded Results

All scarring metrics are strictly bounded between `0.0` and `1.0`. The stub ensures that while environmental degradation increases friction, it does not create unrecoverable states (soft-locks) for the player.

## Non-Visual Boundary

This stub is strictly responsible for **calculating and reporting environmental stain**. It does not handle:
*   Visual terrain deformation.
*   Real-time mutation animations.
*   Automatic deletion of footholds (handled by Upkeep/Reclamation).
