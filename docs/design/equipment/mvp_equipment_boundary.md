# MVP Equipment Boundary

This document defines the foundational framework for bounded equipment in the Tower Engine.

## Philosophy: Operational Strategy vs. Stat Inflation

In the Tower Engine, equipment is not designed for runaway power escalation or "stat-checking" enemies. Instead, equipment is an **operational framework** that alters how the player interacts with the Tower's core pressures:

1.  **Consequence Preservation**: Equipment must never remove the inherent risks of the Tower (e.g., residue, mutation, defeat).
2.  **Tradeoff-Driven**: Every advantage provided by gear (e.g., higher damage, better stability) must introduce a corresponding pressure (e.g., higher visibility, increased repair costs, capacity limits).
3.  **Compounding Maintenance**: Gear is a resource sink. It degrades over time and requires maintenance, reinforcing the "net economy" established in Stage 006.

## Equipment Axes

Equipment is measured along several key operational axes:

*   **Durability**: The structural integrity of the item. It must degrade to ensure ongoing economic pressure.
*   **Repair Pressure**: How much "upkeep wealth" the item consumes per use/maintenance cycle.
*   **Mutation Affinity**: How the item interacts with floor mutations (can potentially stabilize or destabilize).
*   **Residue Visibility**: High-power gear makes the player more "visible" to the Tower, increasing counter-pressure.
*   **Capacity Pressure**: The physical burden of carrying the item, limiting flexibility.
*   **Risk Profile**: The inherent volatility or reliability of the item's effects.

## Bounded Equipment Rules (Anti-Power-Creep)

To maintain engine integrity, all equipment must adhere to these strict bounds:

*   **No Invulnerability**: Gear may absorb pressure but never grant permanent invulnerability.
*   **No Infinite Scaling**: Mathematical scaling must be bounded and non-recursive.
*   **No Residue Bypass**: Gear cannot prevent the generation of residue from player actions.
*   **No Defeat Cancellation**: Equipment may delay or mitigate defeat but cannot bypass the `DEFEAT_DROP` consequence.

## Operational Categories

*   **Weapons**: Project combat strategy.
*   **Armor**: Absorb pressure at the cost of high upkeep.
*   **Mobility Gear**: Modify route and escape options.
*   **Mutation Tools**: Actively interact with or suppress replay mutations.
*   **Stability Focus Items**: Manage floor and domain stability.
*   **Residue Sensitive Items**: High-power items that carry extreme visibility tradeoffs.
