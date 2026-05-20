# Procedural Survivor Markets and Resource Exchange

## Overview
Stage 046 establishes the infrastructure for bounded asynchronous trading in the Tower ecosystem. This system allows survivors to exchange resources, residue artifacts, and world tokens through distributed market relays without creating a centralized auction house or enabling pay-to-win mechanics.

## Market Boundary
The `engine/domain/contracts/market_boundary.json` defines the strict safety rules:
- **Asynchronous Only**: Trade is never instantaneous or real-time; it relies on distributed relay synchronization.
- **Pressure Coupling**: Trade visibility is not free. Large or frequent transactions increase "Tower Attention" and market instability.
- **Anti-Monopoly**: Controls like listing decay and storage pressure prevent resource hoarding and market domination.
- **No Real Money**: Progression is strictly residue-driven; no real-world currency or pay-to-win shortcuts are permitted.

## Resource Exchange Contract
The exchange contract (`engine/domain/contracts/resource_exchange_contract.json`) specifies the required state for a market listing:
1. **Resource Profile**: Detailed breakdown of the items being offered (e.g., residue weight, artifact lineage).
2. **Trade Lineage**: Tracks the history of an artifact across multiple owners to preserve its value and "scars."
3. **Instability Modifiers**: Real-time metrics that scale the visibility and cost of a trade based on current Tower pressure.

## Market Manager
The `engine/domain/market_manager.py` component manages the trade lifecycle:
1. **Listing Creation**: Produces hash-verified, bounded market entries.
2. **Instability Simulation**: Calculates how high Tower pressure affects trade costs and visibility.
3. **Lineage Preservation**: Ensures that residue artifacts carry their history into every transaction.

## Anti-Monopoly Policies
The `anti_monopoly_boundary.json` enforces fairness through:
- **Listing Decay**: Unsold listings lose value or visibility over time.
- **Hoarding Limits**: Survivors are restricted in the number of active listings they can maintain.
- **Distributed Preference**: The system favors local or treaty-based relays over global visibility to reduce systemic risk.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `market status` and `market audit` commands to monitor trade activity and market stability.
- **Dashboard**: The player dashboard provides a lore-compatible view of "Market Flux" and the "Residue Value" of their active trades.

## Conclusion
The Procedural Survivor Market system adds a complex strategic layer to Damian. It encourages resource circulation and coordination among survivors while strictly adhering to the Tower's decentralised and pressure-sensitive architecture.
