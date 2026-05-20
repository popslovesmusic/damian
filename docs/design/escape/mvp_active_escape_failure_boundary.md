# MVP Active Escape Failure Boundary

This document defines the foundational framework for failed escape attempts in the Tower Engine.

## Philosophy: Consequence, not Cruelty

In the Tower Engine, retreating to safety is a core strategic pillar, but it is not a "free" or guaranteed action. The **Escape Failure** system turns retreat pressure into material consequence, ensuring that every spatial decision strengthens the recursive survival loop without making progress impossible or creating unrecoverable dead states.

## Escape Outcomes

When a player attempts to escape (retreat) from a floor, the system resolves the attempt into one of several bounded outcomes:

1.  **ESCAPE_SUCCESS**: The player retreats safely without additional cost.
2.  **ESCAPE_PARTIAL**: The player retreats but suffers a minor consequence (e.g., small resource loss).
3.  **ESCAPE_FAILED_RETREAT_DROP**: The retreat is so hazardous that the player "drops" rather than retreats, potentially incurring a mutation or losing progress.
4.  **ESCAPE_FAILED_PRESSURE_SPIKE**: The attempt triggers an environmental reaction, increasing the floor's mutation pressure or path instability.
5.  **ESCAPE_FAILED_RESOURCE_LOSS**: The player is forced to abandon supplies or gear condition is significantly worsened during the flee attempt.

## Bounded Failure Consequences

To ensure game balance and player recoverability, failed escapes follow these rules:

*   **Write Escape Residue**: Every significant flee attempt (regardless of success or failure) writes residue to the floor, marking the strategic "effort" of the journey.
*   **Support Mutation Pressure**: Environmental instability materially increases the risk of escape failure, coupling floor history to spatial safety.
*   **Preserve Recoverability**: A failed escape must not result in an unrecoverable "dead state." The player should always have a clear, if hazardous, path to continue or attempt a recovery.
*   **Floor Identity Preservation**: Consequences must not delete the recognizable structure of the floor. They should "scar" the paths rather than destroy the topological map.

## Identity Rules

*   **No Permanent Loss**: A failed escape must not permanently delete unique items or player progression that cannot be recovered through future play.
*   **Material Visibility**: Every failed escape and the resulting consequences must be materially visible and auditable in session transcripts.
*   **Recursive Pressure**: The system must reinforce that the further a player pushes their luck, the more hazardous the journey home becomes.

## Future Path

In future patches, this boundary will be implemented as a functional Resolution Stub. The `escape` console command will be updated to trigger these active consequences, materially closing the loop between spatial navigation and the Tower's material economy.
