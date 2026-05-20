# Console Escape Resolution Integration

This document explains the integration of the bounded escape resolution stub into the console `escape` command.

## Overview

The `escape` command has been updated to move beyond guaranteed safety. It now resolves retreat attempts through the **Escape Resolution Stub**, materially connecting spatial risk to retreat consequences. This ensures that every attempt to flee the Tower is a calculated strategic gamble with reviewable outcomes.

## Integration Flow

1.  **Risk Assessment**: When the player executes the `escape` command, the console first calculates the current **Escape Risk** and **Route Exposure** via the `traversal_pressure_stub`.
2.  **Outcome Resolution**: These values are passed to the `escape_resolution_stub.resolve_escape_attempt`, which determines the specific outcome (e.g., `ESCAPE_SUCCESS`, `ESCAPE_PARTIAL`, or `ESCAPE_FAILED_RETREAT_DROP`).
3.  **Consequence Execution**: The resolution result is routed through the `mvp_outcome_pipeline`. This ensures that:
    *   `RETREAT_TO_HUB` outcomes correctly update the current floor to 0.
    *   `DEFEAT_DROP` outcomes (severe escape failure) correctly trigger mutations and survivor mark attachment.
    *   Residue is written for all significant retreat attempts.
4.  **Payload Reporting**: The command payload is populated with comprehensive evidence of the escape, including the resolution record, material losses, and mutation pressure spikes.

## Bounded Consequences

*   **Finite Material Loss**: Failed retreats can result in gold or supply loss, representing the cost of a hindered flight.
*   **Forced Drop**: In extreme cases (high risk and high exposure), a failed escape can result in a "Retreat Drop," where the player is intercepted and forced down a floor, mirroring a combat defeat.
*   **Auditability**: Every step of the resolution process is recorded, ensuring that spatial risk is as auditable as tactical combat in post-session transcripts.

## Strategic Significance

By materially grounding the `escape` command, the "Tower" forces the player to consider their material burden *before* things get desperate. A player carrying a massive hoard of loot will see their escape risk spike, forcing a choice between a risky push for more or a safer, early retreat while they still have the mobility to succeed.
