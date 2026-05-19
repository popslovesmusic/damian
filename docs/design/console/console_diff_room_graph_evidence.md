# Console Diff Room Graph Evidence

## Overview
The `diff` command in the Project Damian text console has been extended to provide topological insights into floor mutations. In addition to reporting changes in floor memory (visits, deaths, mutation levels), the command now includes **Room Graph Mutation Evidence**.

## Topological Reporting
When a player is defeated (`defeat` or `combat dangerous`), the tower applies mutations to the current floor. The `diff` command surfaces these structural changes by comparing the room graph "before" and "after" the mutation.

### Integrated Indicators
- **Graph Structural Changes**: Reports when the underlying topological map has shifted (e.g., `Room graph layout mutated (Level delta: 1)`).
- **Survivor Mark Manifestation**: Explicitly notifies the player when a new survivor mark room has been added to the floor layout (e.g., `A new survivor mark room has been manifested in the graph.`).
- **Validation Status**: Confirms that floor identity anchors and critical path playability have been preserved despite the mutations.

## Data Integration
The integration leverages several engine components:
- `replay_floor_diff_reporter`: For base floor memory comparison.
- `room_graph_mutation_evidence`: For topological analysis.
- `floor_record_builder`: For generating the necessary floor metadata to drive the room graph builders.

## Non-Playable Boundary
Surfacing room graph evidence in the console maintains the project's non-playable boundary. It provides the player with a "logical map" of the tower's response to their actions without requiring real-time navigation, rendering, or pathfinding.

## Usage
After a defeat, simply type `diff` in the console to see a combined report of statistical and topological changes.
