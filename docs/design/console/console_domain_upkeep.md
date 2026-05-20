# Console Domain Upkeep

This document explains the integration of territory maintenance into the MVP Text Console.

## Overview

Establishing a foothold is only the first step. To maintain the strategic benefits of order within the Tower, players must actively manage their territory using the `maintain` command. This requires a constant influx of **Stability Shards** to counteract the Tower's natural entropy.

## The `maintain` Command

The `maintain` command allows players to process upkeep for all established domain footholds in their current session.

*   **Usage**: `maintain`
*   **Behavior**:
    1.  Calculates the required Stability Shards for all active claims.
    2.  Materially deducts the shards from the player's meta-inventory.
    3.  If shards are insufficient, established footholds will begin to **Decay**.
    4.  If upkeep is paid for a decaying foothold, its state is restored to **Active**.

## Decay and Strategic Risk

Failure to maintain territory has material consequences:

*   **DECAYING**: Footholds in this state attract more environmental hostility (increased Visibility Pressure) and provide reduced strategic support.
*   **OVERRUN**: If a decaying foothold is not maintained, it becomes overrun. All strategic benefits are lost, and the node may revert to a hazardous state or trigger a specific mutation.

## Strategic Cognition

By requiring manual maintenance via the console, the "Tower" forces the player to treat territory as a dynamic, resource-intensive investment. Players must decide whether to continue pushing deeper into the Tower or spend their hard-earned shards to stabilize their current footholds.

## Scope Containment

*   **No Automation**: Maintenance is a manual strategic task performed via the `maintain` command.
*   **Data-Driven**: Decay is represented through state changes and pressure metrics, not visual ruins or rendered environments.
*   **Non-Spatial**: Maintenance focuses on the "net economy" of shards and states, rather than physical construction or base-building.
