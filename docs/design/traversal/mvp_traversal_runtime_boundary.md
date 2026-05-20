# MVP Traversal Runtime Boundary

This document defines the foundational framework for bounded traversal in the Tower Engine.

## Philosophy: Operational Burden vs. Movement Animation

In the Tower Engine, traversal is not about "moving a character on a map." Instead, it is a **mechanical strategic exposure** that reinforces the engine's core principles:

1.  **Material Movement Burden**: Every step (advance or retreat) carries an operational cost. Traversal is the mechanism that translates spatial distance into material drain (e.g., stamina, items, durability).
2.  **Escape Tension**: Retreating from a floor is not a "free" or guaranteed action. It carries inherent risk and exposure, which scales with the player's material burden (inventory capacity) and the environmental instability (mutations).
3.  **Route Consequence**: The choice of route determines the level of combat exposure and repair burden the gear will suffer. Deeper exploration is not just about reaching a floor, but about surviving the exposure of the journey.

## Traversal Pressure

Traversal is measured by several key material factors:

*   **Capacity Pressure**: The physical burden of held items makes movement more taxing and escapes more difficult.
*   **Mutation Pressure**: Environmental instability from replay mutations makes routes more unpredictable and dangerous.
*   **Combat Exposure**: The likelihood of being forced into combat encounters during the journey.
*   **Repair Burden**: The aggregate wear placed on gear condition during the journey.

## Identity Rules (Consequence Preservation)

To maintain engine integrity, the traversal system follows these strict rules:

*   **No Free Escape**: Retreating or escaping never bypasses the consequences of progress or the material costs already incurred.
*   **No Defeat Cancellation**: Traversal gear or skills cannot prevent the material reality of `DEFEAT_DROP`.
*   **Recursive Pressure**: Traversal must strengthen, not weaken, the recursive survival loop by making every spatial decision a material strategic tradeoff.
*   **Bounded Visibility**: Traversal exposure remains observable and reviewable in transcripts, ensuring that the "journey" is as auditable as the "battle."

## Future Path

In future patches, this boundary will be implemented as a functional runtime stub. The `ascend` and `retreat` console commands will be updated to trigger traversal events, materially connecting spatial movement to the material economy established in Stages 008 and 009.
