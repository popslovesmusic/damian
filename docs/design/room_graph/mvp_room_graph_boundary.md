# MVP Procedural Room Graph Boundary

## Overview
The MVP Procedural Room Graph Boundary defines the logical structure of floor layouts within Project Damian. It establishes a connected graph of room nodes that represent the topological map of a floor, without implementing actual map generation, navigation, or rendering.

## Continuity Philosophy
Floor identity must be preserved across mutations. When a player re-enters a floor after a defeat, the room graph may shift, but the core "identity" of the floor (archetype, critical path difficulty, key landmarks) must remain recognizable.

### Identity Preservation Rules
- **Structural Persistence**: The core topology should remain similar enough that a player can "learn" the floor's general layout across multiple runs.
- **Mutation Continuity**: Mutations change the connections or properties of nodes (e.g., shifting a corridor, rotating a room's role) without destroying the overall connectivity.
- **Replay Recognition**: Replay floors must support recursive mutation while maintaining the original floor's signature elements.

## Bounded Procedural Generation
This framework focus on the **graphical representation** of floor layouts.

### Core Constraints
- **Connected Graphs**: All graphs must ensure a valid path from the entry node to the exit node.
- **Reachable Exit**: The exit must always be reachable from the entry point, regardless of mutation level.
- **Bounded Branching**: To maintain gameplay pace, branching paths are limited by the floor's depth and domain archetype.
- **Survival Paths**: Every floor must offer a minimum of one recovery path (lower difficulty) and one pressure path (higher difficulty/reward).

## Survivor Mark Integration
Room graphs explicitly support the placement of **Survivor Marks**. Specific room types (`survivor_mark_room`) are designated as valid locations for these marks, ensuring they remain discoverable even as the floor layout mutates.

## Scope Boundaries
The current implementation is limited to **logical graph definitions** and **contract validation**. The following systems are explicitly **OUT OF SCOPE**:
- Playable map generation (tiles, geometry).
- Real-time navigation and pathfinding.
- Visual rendering of rooms or corridors.
- Enemy spawning logic.
- GPU-accelerated layout calculations.
