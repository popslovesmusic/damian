# Stage 008: Inventory Runtime and Material Burden Foundations Review

## Overview
Stage 008 transformed the previously "phantom" economy into a material stratégico burden. This involved implementing a deterministic inventory transaction stub, calculating accumulated capacity pressure, and integrating material deductions for consumables (potions) and maintenance (repair materials) into the console and automated transcripts.

## Identity Status
**STRONG ALIGNMENT**
The "phantom economy" has been materialized. Inventory now acts as a tangible strategic constraint via capacity pressure and atomic safe-failure transactions. The system adheres to the core principle: **reward does not erase consequence**, as hoarded wealth becomes a physical burden that gates strategic flexibility.

## Major Strengths
1.  **Materialized Economy:** Consumable and repair material drains are now material deductions from a persistent inventory state, ensuring that survival has a measurable cost.
2.  **Accumulated Burden:** Capacity pressure effectively translates held items into a 0.0-1.0 metric of strategic burden, making the "bag space" tradeoff immediate and observable.
3.  **Strategic Safe-Failure:** The "All-or-Nothing" transaction logic enforces material limits (specifically capacity) without corrupting the player's state or allowing infinite hoarding.
4.  **Auditability:** Every material change is recorded as a structured `InventoryTransaction`, providing a deep and reviewable evidence trail in console transcripts.

## Major Risks
1.  **The "Hard Cap Cliff":** Capacity pressure currently only blocks transactions at exactly 100% full. Players may not feel intermediate mechanical pressure (e.g., combat penalties) until they hit this cliff.
2.  **Durability Disconnect:** While repair materials are now materially deducted, the equipment themselves do not yet actively degrade or restore durability. The loop is strategically closed but mechanically pending.
3.  **Mental Tracking Burden:** Managing material resources via CLI commands without a visual inventory UI may increase the cognitive load for non-scripted testing.

## Balance Questions
*   Does a flat 40-capacity limit provide the intended estratégico tension across all content types?
*   Should carrying a "HIGH" or "FULL" capacity band mechanically increase the risk of `DEFEAT_DROP` or reduce retreat chances in combat?
*   Should specialized items (e.g., Heavy vs. Light) have variable `capacity_cost` to further differentiate loadouts?

## Required Follow-ups
1.  **Implement Durability Decay:** Gear must degrade during combat to create the demand for the `repair` command.
2.  **Implement Durability Restoration:** Transition the `repair` command from a simple resource drain to a material restoration of equipment durability.
3.  **Capacity Combat Biasing:** Integrate the `capacity_pressure` band into combat resolution outcomes to penalize overloaded players.

## Next Stage Recommendation
Proceed to **Stage 009: Equipment Runtime and Durability Decay**. Now that resources are materially tracked, we must finalize the maintenance loop by implementing active equipment degradation and restoration logic.
