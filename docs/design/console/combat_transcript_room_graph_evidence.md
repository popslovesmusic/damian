# Combat Transcript Room Graph Evidence

## Overview
The Combat-Aware Console Transcript has been enhanced to capture topological evidence of tower mutations. When a console session includes combat encounters that result in a `DEFEAT_DROP` outcome, the transcript now records the resulting **Room Graph Mutation Evidence**.

## Evidence Capture Mechanism
The transcript reporter monitors the results of the `diff` command. If a `diff` command follows a defeat-triggered mutation, the reporter extracts the topological shifts and stores them within the transcript artifact.

### Captured Topological Data
- **Room Graph Evidence Observed**: A boolean flag indicating if topological evidence was successfully captured during the session.
- **Room Graph Changes Observed**: A counter tracking how many structural mutations (graph-level changes) were detected across all `diff` reports.
- **Survivor Mark Rooms Observed**: A counter tracking how many new survivor mark rooms were manifested in the tower graph.
- **Graph Diff Summaries**: A collection of all human-readable topological change summaries generated during the session.

## Integration with Combat Pipeline
This enhancement ensures that the long-term record of a player's journey (the transcript) includes not only statistical changes (health lost, residues gained) but also the logical transformation of the tower's layout. It provides a "topological history" of how the player's defeats have physically reshaped the tower's connectivity.

## Non-Playable Integrity
Consistent with the engine's boundary rules, this evidence is strictly topological. The transcript remains a record of data structures and logical states, preserving the non-playable and non-rendered constraints of the project's current phase.
