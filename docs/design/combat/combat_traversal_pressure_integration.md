# Combat Traversal Pressure Integration

This document explains how spatial traversal pressure and escape risk bias combat outcomes within the Tower Engine.

## Overview

In the Tower Engine, combat does not exist in a spatial vacuum. The hazard of the "journey" (traversal) materially influences the difficulty and results of individual encounters. This ensures that a player who is over-encumbered, unstable, or poorly maintained is more likely to face severe consequences during combat resolution.

## Bias Factors

The combat resolution stub now incorporates the following traversal evidence:

1.  **Route Exposure**: High environmental exposure (from the chosen path) increases the overall environmental hazard. If enemy pressure is also high, this can lead to a significant increase in **effective pressure**, potentially pushing a "Victory" toward a "Defeat."
2.  **Escape Risk**: A high peak risk of failing a retreat makes the player more vulnerable during combat. If the player's health is already low, high escape risk further increases the likelihood of a `DEFEAT_DROP`.
3.  **Traversal Pressure**: The aggregate strategic burden of movement (including inventory weight and mutation instability) acts as a multiplier for **Resource Pressure**. High traversal pressure implies that the player is using more supplies just to stay mobile, making them more likely to run out of potions or reach a forced retreat threshold sooner.

## Identity Preservation

*   **Bounded Biases**: All traversal biases are strictly bounded and cannot create impossible outcomes or bypass the engine's anti-inflation rules.
*   **Pipeline Integrity**: Combat outcomes continue to be routed through the `mvp_outcome_pipeline`. Traversal pressure may bias the *choice* of outcome (e.g., forcing a retreat), but it does not bypass the material consequences (residue, progression) associated with that outcome.
*   **Visibility**: Every bias applied during resolution is recorded in the `traversal_bias_reasoning` array, ensuring that the "why" of a defeat or retreat is always materially reviewable in session transcripts.

## Strategic Significance

By coupling traversal and combat, the "Tower" creates a unified strategic pressure. A player cannot ignore the weight of their inventory or the instability of the floor just because they are good at combat. Eventually, the material burden of the journey will catch up to them, forcing a choice between a risky advance or a strategic retreat to safety.
