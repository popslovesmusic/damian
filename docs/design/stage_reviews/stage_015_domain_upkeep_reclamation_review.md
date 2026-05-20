# Stage 015: Domain Upkeep and Tower Reclamation Pressure Review

## Overview
Stage 015 transitioned Domain Ownership from passive strategic footholds into active operational burdens. This involved implementing the material cost of maintaining order (Stability Shard upkeep), a deterministic decay state machine for neglected territory, and the environmental counter-force known as **Reclamation Pressure**.

## Identity Status
**STRONG ALIGNMENT**
The "net economy" of territory ownership is now materially realized. By requiring the continuous expenditure of resources and inviting escalating environmental pushback, the engine reinforces its core identity: **Order is an artificial state that must be maintained at a cost.** The system successfully avoids the "safe base" trope, ensuring that even established territory remains a source of strategic tension.

## Major Strengths
1.  **Material Strategic Tradeoffs:** The introduction of Stability Shard upkeep forces players to choose between expansion and stabilization.
2.  **Deterministic Decay:** The Active -> Decaying -> Overrun state machine provides a clear, auditable consequence for resource neglect.
3.  **Dynamic Environmental Response:** Reclamation Pressure successfully aggregates visibility, decay, and depth into a unified hazard metric that influences mutation bias.
4.  **Survival Cognition Infrastructure:** Perfectly integrated with the Domain Dashboard, surfacing reclamation threat levels (STABLE to CRITICAL) for informed decision-making.
5.  **Audit Maturity:** Transcripts now capture the longitudinal struggle between Order and Entropy, providing a rich data set for longitudinal balance analysis.

## Major Risks
1.  **Shard Scarcity/Inflation:** If Stability Shard drop rates are not carefully tuned, territory management could become either impossible (scarcity) or trivial (inflation).
2.  **Micro-management Fatigue:** As the number of footholds grows, the manual `maintain` command might become tedious.
3.  **State Complexity:** The interaction between "Overrun" footholds and local mutation hazards needs to be carefully handled in the next stage to ensure it strengthens recursive memory without creating soft-locks.

## Balance Questions
*   Is the upkeep cost scaling (every 3 floors) sufficient to discourage "infinite expansion"?
*   Does "Visibility Pressure" generate enough Reclamation irritation to make high-value outposts feel risky?
*   Should OVERRUN footholds provide a unique "Residue Bonus" to the Tower's reclamation drive?

## Required Follow-ups
1.  **Implement Mutation Scarring and Claim Targeting (Stage 016):** Develop the actual mutation behaviors that target decaying or high-visibility footholds.
2.  **Refine Reclamation Heuristics:** Incorporate the history of successful reclamation into future pressure calculations.
3.  **Stability Shard Economy Audit:** Perform a simulated run audit to determine the "Order Carrying Capacity" of the current shard drop rates.

## Next Stage Recommendation
Proceed to **Stage 016: Mutation Scarring and Claim Targeting**. Now that we have defined the pressures and decay states, we must implement the physical consequences of the Tower's reclamation—the "scarring" of the environment and the direct targeting of established footholds by mutations.
