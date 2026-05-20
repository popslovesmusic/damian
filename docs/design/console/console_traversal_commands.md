# Console Traversal Commands

This document explains the bounded traversal commands (`advance` and `escape`) within the MVP Text Console.

## Overview

The `advance` and `escape` commands materialize spatial movement as a series of strategic tradeoffs. Unlike the legacy `ascend` and `retreat` commands (which remain supported for backward compatibility), these commands incorporate the **Traversal Pressure** and **Escape Risk** calculated from the player's material burden.

## Commands

### `advance`

*   **Description**: Attempt to move from the current floor to the next floor (ascending).
*   **Behavior**:
    1.  Gathers current material factors (capacity, gear condition, mutations).
    2.  Calculates **Traversal Pressure** and **Route Exposure** via `traversal_pressure_stub`.
    3.  If successful, routes the player through the `VICTORY_ASCEND` outcome pipeline.
    4.  Respects the MVP limit (currently 3 floors).
*   **Significance**: Every advance now carries the "weight" of the items held in the inventory, making deeper exploration more hazardous.

### `escape`

*   **Description**: Attempt to retreat from the current floor back to the Hub (floor 0).
*   **Behavior**:
    1.  Gathers current material factors.
    2.  Calculates **Escape Risk** via `traversal_pressure_stub`.
    3.  If successful, routes the player through the `RETREAT_TO_HUB` outcome pipeline.
*   **Significance**: Returning to safety is not a "free" action. It is a strategic escape that becomes more difficult when the player is over-encumbered or gear is broken.

## Strategic Observability

Both commands return a structured payload containing a `TraversalEvent`. This ensures that every spatial decision—and the risks associated with it—is materially recorded in session transcripts for audit and review.

## Non-Movement Scope

These commands remain strictly within the engine's mechanical boundary. They do not:
*   Animate character movement.
*   Require or render a map.
*   Perform real-time pathfinding.
