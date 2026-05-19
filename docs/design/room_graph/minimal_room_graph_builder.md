# Minimal Deterministic Room Graph Builder

## Overview
The Minimal Room Graph Builder is a deterministic runtime component responsible for generating logical room graph records from floor metadata. It serves as the foundation for the procedural generation pipeline within the non-playable boundary.

## Determinism
To ensure that floor layouts remain consistent across different sessions (until explicitly mutated), the builder is designed to be deterministic. Given the same `floor_id` and `domain_archetype`, it will always produce the same graph structure.

### Seeded Generation
While the current MVP uses a fixed shape, future iterations will utilize the `layout_seed` derived from the `floor_id` to drive variety while maintaining determinism.

## Graph Topology
The builder constructs a connected graph with specific node types:
- **Entry Room**: The starting point of the floor.
- **Combat Room**: The initial encounter.
- **Pressure/Recovery Branch**: A tactical choice for the player (high risk/reward vs. safety).
- **Survivor Mark Room** (Optional): A room specifically designated for survivor mark discovery.
- **Exit Room**: The completion point of the floor.

## Non-Playable Boundary
This builder strictly operates within the logical domain. It produces data structures that describe the *topology* of the floor, not the *geometry*.
- **No Tiles**: It does not place floor tiles or walls.
- **No Navigation**: It does not implement AI pathfinding.
- **No Physics**: There is no collision or spatial simulation.

## Failure Handling
The builder uses a structured error pattern to ensure that failures (e.g., unsupported archetypes, schema violations) are reported clearly without crashing the engine runtime.

## Debug Hooks
Built-in debug hooks allow for logging the generation process when enabled, facilitating troubleshooting without impacting production performance.
