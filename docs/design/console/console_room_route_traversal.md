# Console Room Route Traversal

This document explains the integration of topological room traversal routes into the console `advance` and `escape` commands.

## Overview

The `advance` and `escape` commands have been upgraded from abstract floor-to-floor jumps to **route-aware spatial choices**. When a player attempts to move, the console now builds a logical room graph for the current floor and generates specific material routes between rooms.

This ensures that spatial navigation is materially grounded in the Tower's topography, turning every journey into a series of strategic tradeoffs.

## Command Behavior

### `advance`

*   **Topological Assessment**: The command builds or loads the current floor's `RoomGraph`.
*   **Route Generation**: It uses the `room_traversal_route_builder` to generate unique hazards (darkness, instability, etc.) for all node connections.
*   **Path Selection**: The system automatically selects a `primary_route` or `pressure_route` to represent the journey to the next floor.
*   **Hazard Calculation**: The selected route's exposure and profile materially influence the **Traversal Pressure**, making the advance harder if the chosen path is hazardous.
*   **Outcome**: Successful advances continue to route through the `VICTORY_ASCEND` pipeline, respecting the MVP content boundary.

### `escape`

*   **Topological Assessment**: Similar to advance, it builds the current floor's topography.
*   **Path Selection**: The command specifically looks for `escape_route` or `recovery_route` types, which represent safer paths back to the Hub.
*   **Risk Mitigation**: The route's `escape_modifier` directly influences the **Escape Risk**. Retreating through a dedicated escape path is materially safer than fleeing through an active combat room.
*   **Outcome**: Successful escapes route through the `RETREAT_TO_HUB` pipeline.

## Strategic Observability

The command payloads now include the full `RoomGraph` and the set of generated `RoomTraversalRoutes`. This ensures that spatial decisions are recorded as material strategic evidence in session transcripts, allowing auditors to see how topological hazards influenced the player's journey and combat outcomes.

## Non-Map Boundary

Spatial navigation remains strictly mechanical. The system uses logical graph connections and environmental profiles to calculate hazard, avoiding the scope creep of rendered maps, pathfinding algorithms, or real-time character movement.
