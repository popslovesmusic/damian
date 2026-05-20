# Stage 011: Room Traversal Graph Runtime Boundary Review

## Overview
Stage 011 focused on replacing abstract "floor-to-floor" jumps with topological "room-to-room" navigation. This involved defining a deterministic route builder that creates Environmental Profiles (darkness, instability, enemy exposure) for graph connections. We integrated these routes into console commands and used their specific hazards to materially bias combat outcomes—all while strictly avoiding map rendering, real-time movement, or pathfinding.

## Identity Status
**STRONG ALIGNMENT**
Spatiality is no longer an abstract concept. The Tower now has "terrain" in the form of topological strategic hazards that materially influence tactical decisions and resource consumption. The system enforces the principle that **every spatial choice carries a physical and auditable consequence**.

## Major Strengths
1.  **Topological Strategic Choice**: The distinction between "Pressure Routes" and "Recovery Routes" creates a new layer of meaningful decision-making.
2.  **Environmental Granularity**: Profiles like Darkness, Instability, and Mutation Scarring turn simple graph connections into hazardous corridors, reinforcing the engine's "compounding hazard" identity.
3.  **Risk-Coupled Navigation**: Retreating is now materially safer through specific routes (e.g. Escape Routes), providing a legitimate tactical reason to consider exit paths before the pressure peaks.
4.  **Strategic Observability**: Every topological hazard and the specific route chosen for navigation are granularly captured in transcripts, allowing for deep post-session strategic review.
5.  **Clean Scope Containment**: Successfully materialized spatiality using only graph logic and environmental profiles, avoiding the complexity of rendered maps.

## Major Risks
1.  **Automatic Selection Bias**: Currently, the console automatically selects the most appropriate route (e.g., primary for advance, escape for retreat). To be truly strategic, the player needs to make these choices manually.
2.  **Static Profile Generation**: Route profiles are currently derived only from node difficulty and mutation level. They do not yet react dynamically to the volume of residue previously written to that specific path.
3.  **Abstract Progress**: While rooms exist, the transition between them is still instantaneous. There is no "journey time" or "interim encounter" logic to further materialize the distance between rooms.

## Balance Questions
*   Should the `darkness` environmental profile require specific material consumption (e.g., torches) to prevent it from dominating the traversal hazard?
*   How much should `mutation_scarring` increase combat risk vs. simply setting the `residue_pressure_observed` flag?
*   Are "Pressure Routes" rewarding enough (in terms of loot or progress) to justify their significantly higher defeat risk?

## Required Follow-ups
1.  **Implement Manual Route Selection**: Update console traversal commands to present the player with multiple topological choices.
2.  **Define Active Escape Failure**: Define the mechanical reality of what happens when a high `escape_risk` manifests as a failure (e.g., being cornered).
3.  **Residue-Route Coupling**: Allow written residue to materially alter the environmental profile of the route it was written on, creating permanent "scars" on the floor topology.

## Next Stage Recommendation
Proceed to **Stage 012: Define MVP Active Escape Failure Boundary**. Now that spatial choices are coupled with hazard and risk, we must define the mechanical consequences of that risk failing, further strengthening the Tower's recursive survival loop.
