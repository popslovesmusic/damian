# Faction Schisms and Survivor Politics

## Overview
Stage 049 defines the infrastructure for political instability and evolution within procedural survivor blocs. In the Tower, cooperation is a strategic choice under pressure, and factions are subject to "Faction Schisms"—procedural split events triggered by scarcity, betrayal, or relay instability. This system models how ideological residue and political strain reshape the social landscape without enabling permanent player governments or irreversible social exile.

## Schism Boundary
The `engine/domain/contracts/faction_schism_boundary.json` defines the strict safety rules:
- **No Permanent Exile**: Political outcomes cannot permanently lock survivors out of the system or social interactions.
- **Bounded Audit**: Every schism and splinter event is hash-verified and recorded in system lineage audits.
- **Recoverability Mandatory**: Every political crisis must include defined recovery or reconciliation paths (e.g., trust-repair quests, shared defense).
- **Asynchronous Politics**: Political shifts propagate contextually through the relay network, maintaining the engine's temporal isolation.

## Schism Event Contract
The schism contract (`engine/domain/contracts/schism_event_contract.json`) specifies the required state for a political split:
1. **Trigger Source**: Identifies the systemic cause (e.g., `treaty_betrayal`, `resource_hoarding`).
2. **Ideological Residue**: Tracks the character of the split, creating a lasting "scar" on the faction's history.
3. **Splinter Candidates**: Defines the sub-blocs or splinter groups emerging from the original faction.
4. **Strain Metrics**: Real-time modifiers that increase treaty strain and market instability during a schism.

## Schism Manager
The `engine/domain/schism_manager.py` component manages the political lifecycle:
1. **Schism Generation**: Produces bounded split events based on systemic pressure context.
2. **Splinter Formation**: Manages the division of member IDs into new, strained alliances while preserving individual persistence.
3. **Reconciliation Resolution**: Generates recovery paths that allow factions to rebuild trust or merge after a period of instability.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `politics status` and `politics audit` commands to monitor active schisms and review the history of political recovery.
- **Dashboard**: The player dashboard displays current faction strain, splintering risks, and the "Ideological Residue" of their active alliances.

## Conclusion
The Faction Politics system ensures that social life in the Tower is as dynamic and hazardous as the environmental pressure itself. it fosters complex survivor agency through collective choices and systemic consequences, while strictly protecting the engine's foundational safety and decentralized architecture.
