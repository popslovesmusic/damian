# Stage 006: Economy and Resource Pressure Foundations Review

## Overview
This stage established the foundational "Loot Event Stub" and integrated economic observability into the Console Transcripts. The goal was to simulate the flow of wealth and resources without building full inventory, shop, or crafting systems, ensuring the "net economy" remains bounded and analyzable.

## Identity Status
**STRONG ALIGNMENT**
The implemented stubs successfully enforce the core identity: reward does not erase consequence. By explicitly separating gross income (loot) from estimated costs (resource sink pressure), the system highlights that even victorious ascents come at a compounding structural cost.

## Major Strengths
1.  **Deterministic Bounded Loot:** Ensures rewards are testable, consistent, and completely predictable without requiring complex RNG or generation logic during the MVP phase.
2.  **Explicit Resource Sinks:** Reporting "Resource Sink Pressure" (estimated costs for potions, repairs, upkeep) exposes the hidden costs of combat, making economic balance measurable before shops exist.
3.  **Strict Safety Bounds:** The `bounded_reward_flags_clean` check in transcripts guarantees that no game-breaking power creep (e.g., invulnerability) is accidentally introduced.
4.  **Consequence Preservation:** The economy already reinforces the core identity: reward does not erase consequence.

## Major Risks
1.  **Static Rewards:** Flat deterministic rewards (e.g., exactly 10,000 gold per victory) will feel artificial and fail to stress-test economic variance once actual equipment is introduced.
2.  **"Phantom" Economy Imbalance:** Because resource sink pressure is currently only reported and not mechanically deducted from a player inventory, actual structural imbalances may remain hidden.
3.  **Abstract Sinks:** If resource sinks remain purely abstract numbers, players may not feel the pressure emotionally or strategically. The drain must be visceral.
4.  **Rare Material Scarcity:** Currently, Rare Materials are exclusively granted by claiming Survivor Marks, which could severely bottleneck progression testing.

## Balance Questions
*   Is 10,000 gold per `VICTORY_ASCEND` sufficient to outpace the combined estimated sink pressure (potions + repair + upkeep) over a 10-floor run?
*   Should `DEFEAT_DROP` provide any gold at all, or should failure represent a total economic loss alongside the structural mutation cost?
*   How should we scale estimated resource sink pressure as floor depth and mutation intensity increase?

## Required Follow-ups
1.  **Define MVP Inventory Boundary:** Establish how accumulated wealth is stored and bounded.
2.  **Define MVP Equipment Boundary:** Provide a meaningful structure and sink for the generated wealth.
3.  **Visceral Resource Drain:** Inventory and equipment systems should make resource drain visible through repair mechanics, depletion mechanics, capacity limits, and explicit tradeoff pressure.

## Next Stage Recommendation
Proceed to **Stage 007: MVP Equipment Boundary**. Now that wealth generation is observable and bounded, we must define the structured items and inventory systems that will consume this wealth and provide mechanical leverage (or burden) to the player.
