# Procedural Factions and Autonomous Survivor Blocs

## Overview
Stage 048 defines the social structures of the Tower through "Survivor Blocs"—dynamic, procedural factions that emerge organically from the established systems of treaties, markets, relay hubs, and contract networks. Factions in Damian are not static guilds; they are unstable, pressure-sensitive alliances that thrive or fracture based on shared residue and systemic tradeoffs.

## Faction Boundary
The `engine/domain/contracts/faction_boundary.json` defines the strict safety rules:
- **Emergent Only**: Factions must form based on established player activity (e.g., treaty clusters, shared relay usage).
- **No Governance**: Blocs provide mutual support but never grant players authority over other players' saves or OS-level controls.
- **Interdependence and Attention**: Faction growth is not "free." Larger blocs generate more "Tower Attention," increasing environmental pressure and the risk of adversarial encounters for all members.
- **Recoverable Fracture**: If a bloc becomes too unstable, it can fracture (members leave or sub-groups splinter), but the system ensures that individual player persistence and recoverability are maintained.

## Survivor Bloc Contract
The bloc contract (`engine/domain/contracts/survivor_bloc_contract.json`) specifies the required state for a procedural faction:
1. **Emergence Source**: Identifies the primary system that triggered the bloc's formation (e.g., a high-volume market cluster).
2. **Dominant Residue**: Tracks the shared character or "vibe" of the faction based on member signatures.
3. **Stability and Fracture Pressure**: Real-time metrics that scale based on growth, activity, and external Tower pressure.
4. **Member Profile**: A list of connected survivor IDs participating in the bloc.

## Faction Manager
The `engine/domain/faction_manager.py` component manages the faction lifecycle:
1. **Emergence Detection**: Identifies when clusters of activity reach a threshold for bloc formation.
2. **Stability Calculation**: Models how growth and shared activity increase systemic noise and fracture risk.
3. **Fracture Resolution**: Manages the safe splintering of unstable blocs, ensuring no permanent player lockout or loss of lineage.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `faction status` and `faction audit` commands to monitor emergent social dynamics and systemic stability.
- **Dashboard**: The player dashboard displays active blocs, their "Dominant Signature," and the current "Fracture Risk" associated with their alliances.

## Conclusion
The Procedural Factions system ensures that social cooperation in Damian is as hazardous and dynamic as the Tower itself. It fosters high-level coordination while strictly adhering to the engine's decentralized and safety-first architecture.
