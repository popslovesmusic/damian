# Minimal Tower Reclamation Pressure Stub

This document explains the deterministic implementation of Tower Reclamation Pressure for the Tower Engine MVP.

## Overview

The `tower_reclamation_pressure_stub` calculates the aggregate environmental counter-force exerted by the Tower against established Order. It turns territory management into a risky endeavor by measuring how much environmental "irritation" the player is generating.

## Calculation Factors

Reclamation Pressure is derived from three material factors:

1.  **Visibility Pressure**: Every established foothold attracts attention. The more complex or numerous the footholds, the higher the baseline reclamation drive.
2.  **Order Decay**: Neglected footholds (those in a `DECAYING` state) act as weak points in the fabric of Order, significantly increasing local Reclamation Pressure.
3.  **Tower Depth**: Entropy is stronger deeper in the Tower. The baseline Reclamation Pressure increases every few floors.

## Reclamation Bands

The aggregate pressure (0.0 to 1.0) is classified into descriptive bands that inform player survival cognition:

*   **STABLE**: Minimal resistance. Footholds are safe for now.
*   **IRRITATED**: The Tower has noticed the established order. Minor mutation bias.
*   **HOSTILE**: Active environmental pushback. Significant mutation bias.
*   **VOLATILE**: The Tower is actively attempting to reclaim territory. High risk of foothold degradation.
*   **CRITICAL**: Maximum resistance. Severe environmental consequences are imminent.

## Strategic Impact (Mutation Bias)

Reclamation Pressure directly influences the **Mutation Risk Bias**. Higher reclamation levels increase the probability of mutations that specifically target established order or increase the tactical difficulty of the surrounding floor.

## Non-Wave Defense Boundary

This stub is strictly responsible for **calculating and reporting environmental pressure**. It does not handle:
*   Real-time "wave defense" combat.
*   Physical environmental animations (e.g., creeping vines or shadows).
*   Automatic destruction of buildings.
