# Room Graph Mutation Evidence

## Overview
Room Graph Mutation Evidence provides a topological view of how a floor's layout changes after a mutation event (typically triggered by a `DEFEAT_DROP`). It allows developers and systems to visualize and validate structural changes to the floor graph before any playable map generation or rendering occurs.

## Mutation Lineage
The evidence tracks the transformation of a room graph while preserving its core lineage.
- **Before Graph**: The room graph representing the floor's state prior to the mutation.
- **After Graph**: The room graph representing the floor's state after the mutation.

## Key Transformation Indicators
The integration detects several critical changes:
- **Graph Structural Changes**: Any shift in the connections or node types between the before and after states.
- **Survivor Mark Manifestation**: Specifically identifies when a `survivor_mark_room` is added to the graph, which occurs when a floor gains unclaimed survivor marks.
- **Mutation Level Delta**: Tracks the increase in the floor's mutation level, reflecting the intensity of the transformation.
- **Preservation Validation**: Confirms that despite the mutations, the floor's core identity anchors and entry-to-exit playability remain intact.

## Non-Playable Evidence
Consistent with the project's bounded development philosophy, this evidence remains strictly data-driven and non-playable.
- **No Pathfinding**: Pathfinding is not simulated; only topological connectivity is verified.
- **No Rendering**: No visual representation is generated.
- **Deterministic**: The evidence is derived from deterministic room graph builders, ensuring consistency across similar mutation scenarios.

## Integration Points
- **Replay Outcome Pipeline**: Generated as part of the evidence gathering following a player's defeat.
- **Console Reporting**: Can be surfaced in the text console to show players (or developers) how the tower has shifted in response to their actions.
