# Adaptive Narrative Evolution and World Memory

## Overview
Stage 052 introduces the infrastructure for the Tower's procedural memory. In Damian, the world is not static; it remembers the aggregate residue of survivor actions—treaties, collapses, market instability, and event waves—and uses this data to evolve future world conditions. This "Adaptive Narrative" ensures that the Tower feels historically alive and reactive without relying on traditionally authored, static campaigns.

## Narrative Evolution Boundary
The `engine/domain/contracts/adaptive_narrative_boundary.json` defines the strict safety rules:
- **No Static Canon**: There is no hardcoded "true" history. The Tower's past is reinterpreted through systemic pressure and probabilistic drift.
- **Residue-Based**: All memory must be tied to established game systems (e.g., world scars, relay fragmentation).
- **Anti-Canon Lock**: Systemic mutations must remain bounded to prevent the world from reaching an unplayable or irreversible state.
- **Recoverability Mandatory**: Even as the narrative evolves, the core player experience and recoverability must be preserved.

## World Memory Contract
The memory contract (`engine/domain/contracts/world_memory_contract.json`) specifies the required state for a world memory manifest:
1. **Historical Residue**: Aggregate pressure and instability scores that define the "weight" of the past.
2. **Survivor Action Summary**: High-level metrics of cooperation and conflict (treaties, echoes).
3. **World Scars**: Lasting signatures of major systemic events (e.g., "The Great Splinter").
4. **Narrative Drift Profile**: Tracks the probabilistic direction of procedural mythology.

## Narrative Manager
The `engine/domain/narrative_manager.py` component manages the historical lifecycle:
1. **Residue Aggregation**: Compiles aggregate metrics into hash-verified world memory artifacts.
2. **Procedural Drift**: Simulates how the Tower "reinterprets" its past over time, shifting the emphasis of future procedural generation.
3. **Historical Contract Generation**: Produces dynamic objectives that reflect the world's memory (e.g., quests to repair a scarred relay hub from a previous era).

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `narrative status` and `narrative audit` commands to monitor aggregate world memory and review the history of procedural drift.
- **Dashboard**: The player dashboard provides lore-compatible hints of the "Tower Memory" and how their collective residue is reshaping the world.

## Conclusion
The Adaptive Narrative Evolution system ensures that Damian remains a living, evolving ecosystem. It fosters a sense of collective consequence and history that is as dynamic and hostile as the environmental pressure itself, while strictly protecting the engine's decentralized and safety-first architecture.
