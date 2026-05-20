# Stage 012: Active Escape Failure and Consequence Routing Review

## Overview
Stage 012 focused on defining and implementing the material consequences of failed retreat attempts. This involved establishing the `escape_failure_boundary`, creating a deterministic `escape_resolution_stub`, and integrating it into the console and transcripts. The system ensures that retreating from the Tower is a calculated strategic risk rather than a guaranteed safety valve.

## Identity Status
**STRONG ALIGNMENT**
The spatial risk loop is now materially closed. Retreating from the Tower correctly carries the burden of the player's choices and current material state. The system reinforces that **flight carries cost**, strengthening the recursive survival loop while preserving the engine's core principle that reward does not erase consequence.

## Major Strengths
1.  **Bounded Material Consequences:** Successfully implemented varied failure outcomes (resource loss, pressure spikes, forced drops) that create meaningful pressure without resulting in unrecoverable dead states.
2.  **Pipeline Consistency:** Routing severe escape failures through the `DEFEAT_DROP` pipeline ensures that retreat hazards share the same systemic consequences (mutations, marks) as tactical failures.
3.  **Strategic Transparency:** The use of `escape_risk` and `route_exposure` to resolve outcomes makes the strategic hazard of the journey fully auditable and reviewable in transcripts.
4.  **Residue-Integrated Retreat:** Every escape attempt writes residue, ensuring that the "effort" of a failed or successful flight leaves a material record on the Tower's memory.
5.  **Scope Containment:** Achieved high-tension escape mechanics without the need for real-time chase systems, rendered maps, or AI pathfinding.

## Major Risks
1.  **Static Consequence Scaling:** Current resource loss values are flat (e.g. 250 gold). These may become negligible as the player's wealth grows, requiring a transition to dynamic, percentage-based losses.
2.  **Psychological Friction:** Forced drops during an escape can be highly frustrating. Clearer communication of risk and the introduction of manual route choice are needed to ensure the player feels ownership over their failure.
3.  **Command Redundancy:** Maintaining both the legacy `retreat` (safe) and the new `escape` (risky) commands may cause confusion. Legacy commands should eventually be deprecated or aliases for low-risk escape.

## Balance Questions
*   Should `ESCAPE_FAILED_PRESSURE_SPIKE` outcomes trigger an immediate "Ambush" combat encounter?
*   Should the probability of severe failures (`RETREAT_DROP`) scale exponentially with the player's `over_capacity` status?
*   Are the current risk thresholds (Success <= 0.3) too lenient for a survival-focused engine?

## Required Follow-ups
1.  **Define MVP Domain Dashboard Boundary:** Transition to meta-strategic oversight of these compounding tactical consequences.
2.  **Dynamic Consequence Scaling:** Update the resolution stub to calculate resource losses as a percentage of current inventory.
3.  **Manual Route Selection:** Empower the player to choose between routes with different hazards and escape modifiers, moving from automatic to manual spatial agency.

## Next Stage Recommendation
Proceed to **Stage 013: Define MVP Domain Dashboard Boundary**. Now that the tactical consequences of combat and traversal are materialized and auditable, we must provide a meta-strategic layer to oversee and manage these compounding pressures across the entire Tower.
