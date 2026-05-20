# Stage 009: Equipment Runtime and Durability Decay Review

## Overview
Stage 009 focused on closing the "Compounding Maintenance" loop. This involved implementing deterministic durability decay based on combat and capacity pressure, and creating a material repair runtime that converts inventory resources (Stage 008) into gear condition restoration.

## Identity Status
**STRONG ALIGNMENT**
The maintenance loop is now functionally closed. Equipment condition is a material consequence of Tower exploration, requiring a continuous strategic tradeoff between looting materials and restoring operational longevity. The system adheres to the core principle: **reward does not erase consequence**.

## Major Strengths
1.  **Closed Maintenance Cycle:** Successfully connected material acquisition (loot) with material restoration (repair), making equipment sustainability a central strategic pillar.
2.  **Bounded Restoration Logic:** Fixed restoration amounts and maximum durability caps prevent "free" or infinite gear maintenance, preserving economic tension.
3.  **Zero-Floor Identity Persistence:** Gear reaching 0 durability is not deleted, preserving the item's identity and player investment while signaling a high-risk operational state.
4.  **Audit Trail Clarity:** Individual `DurabilityDecayEvents` and `RepairEvents` are granularly captured in transcripts, allowing for precise auditing of the engine's net economy.

## Major Risks
1.  **Passive Zero-Durability Penalties:** Without a full stat-scaling system, 0-durability gear currently has a "soft" penalty (it just stops decaying). It must eventually actively penalize combat effectiveness to maintain visceral pressure.
2.  **Maintenance Predictability:** The flat 10.0 durability per basic material is highly deterministic and may lead to a mathematical "optimal path" that reduces strategic friction over time.
3.  **Material Oversupply Risk:** If victory loot consistently drops repair materials, the player may never experience the intended "maintenance drought" that forces difficult tradeoffs.

## Balance Questions
*   Should higher-tier items have higher repair costs (more materials) or lower restoration efficiency?
*   Should carrying broken (0 durability) gear increase the player's `risk_profile` during combat resolution?
*   Is the current material drop rate from `VICTORY_ASCEND` too generous for a survival-focused engine?

## Required Follow-ups
1.  **Define MVP Traversal Runtime Boundary:** Introduce spatial resource costs (e.g., food/stamina drain) to complement combat wear.
2.  **Implement Active 0-Durability Penalties:** Ensure broken gear materially harms combat resolution outcomes (e.g., increasing retreat chance).
3.  **Loot Rarity Audit:** Review the `loot_event_stub` to ensure that material scarcity scales appropriately with Tower depth.

## Next Stage Recommendation
Proceed to **Stage 010: MVP Traversal Runtime Boundary**. Now that the maintenance loop for equipment is established, we must extend the material strategic burden to spatial movement and floor-to-floor traversal.
