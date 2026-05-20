# Stage 007: Equipment Pressure Foundations Review

## Overview
Stage 007 established the foundational "Equipment Pressure" framework. The objective was to move away from traditional RPG "stat-stick" gear and instead treat equipment as an operational framework that modifies the Tower's inherent pressures (repair, visibility, risk, and capacity).

## Identity Status
**STRONG ALIGNMENT**
The framework successfully treats equipment as a **modifier of consequence** rather than a **remover of consequence**. The integration into the combat resolution stub proves that gear can influence the probability of retreat or defeat without bypassing the core MVP outcome pipeline.

## Major Strengths
1.  **Tradeoff-First Design:** Gear is measured by its burden (`repair_pressure`, `capacity_pressure`) as much as its utility.
2.  **Deterministic Aggregate Pressure:** The averaging logic in the stub provides a predictable way to measure the "burden of gear" for a player loadout.
3.  **Combat Coupling:** Equipment is mechanically linked to high-level outcomes (e.g., high risk profile biasing defeat, high capacity biasing retreat) rather than just incremental stat buffs.
4.  **Safety Enforced:** Automated validation prevents any equipment from activating bypass flags (invulnerability, residue cancellation).

## Major Risks
1.  **Averaging Dilution:** Calculating the arithmetic mean of item profiles might dilute the unique strategic "spike" of a highly specialized item if paired with mediocre gear.
2.  **Hard Thresholds:** Current combat biasing uses fixed thresholds (e.g., > 0.8 capacity pressure). This may lead to "breakpoints" that feel gamey rather than organic.
3.  **The "Phantom Cost" Problem:** Similar to Stage 006, repair pressure is currently "observed" in transcripts but not yet mechanically deducted from a persistent inventory.
4.  **Drift to Complexity:** While the stub is minimal, there is a risk that as more items are added, the operational profile becomes harder for players to parse at a glance.

## Balance Questions
*   Is a 15% increase in effective pressure from "High Risk" gear too punishing, or just right for the Tower's identity?
*   Should "Mutation Affinity" have a more direct impact on combat resolution, or should it remain a structural-only modifier?
*   Does the "averaging" logic reward carrying empty slots, or should we use a "sum and scale" approach for capacity?

## Required Follow-ups
1.  **Define MVP Inventory Runtime Boundary:** Wealth and repair costs must transition from "reported" to "deducted."
2.  **Equipment Durability Runtime:** Implement the logic that causes gear to degrade based on floor depth and encounter intensity.
3.  **Emotional Visibility:** Ensure that the "cumbersomeness" of high capacity pressure is signaled clearly to the player in transcripts.

## Next Stage Recommendation
Proceed to **Stage 008: MVP Inventory Runtime Boundary**. The "phantom economy" of Stage 006 and Stage 007 must now be consolidated into a persistent, bounded inventory that manages gold, materials, and equipment durability.
