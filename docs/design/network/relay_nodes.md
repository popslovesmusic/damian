# Tower Relay Nodes and Distributed Survivor Hubs

## Overview
Stage 044 defines the infrastructure for distributed social and adversarial exchange in the Tower ecosystem. This system relies on "Relay Nodes"—fragile, survivor-operated hubs that allow for the asynchronous transfer of Domain Echoes, treaty signals, and reputation residue. Unlike a centralized MMO, the Tower network is designed to be partial, pressure-sensitive, and prone to fragmentation.

## Relay Boundary
The `engine/network/contracts/relay_node_boundary.json` defines the strict safety rules:
- **No Centralized Authority**: Relay nodes are decentralized and operated by survivors; no single hub has omniscient control or real-time combat authority.
- **Asynchronous Only**: All message exchange (echoes, signals) is queued and processed asynchronously to maintain the Tower's temporal isolation.
- **Pressure Coupling**: Relay activity is not "free." Increased communication visibility directly increases the "Tower Attention" pressure on the hub and its connected domains.
- **Fragmentation Safe**: High pressure can cause a hub to fragment (degrade or go partially offline), but the system ensures that player state and message queues remain recoverable.

## Relay Hub Contract
The hub contract (`engine/network/contracts/relay_hub_contract.json`) specifies the required state for a relay:
1. **Stability and Attention**: Real-time metrics tracking the hub's operational health and its visibility to the Tower.
2. **Async Queues**: Dedicated buffers for `DomainEcho` and `TreatySignal` exchanges.
3. **Roles**: Bounded hub roles (e.g., `private_relay`, `domain_echo_exchange`) ensure that no hub can evolve into a general-purpose OS control node.

## Relay Manager
The `engine/network/runtime/relay_hub_stub.py` component manages the hub lifecycle:
1. **Hub Creation**: Produces hash-verified, role-bounded relay nodes.
2. **Asynchronous Queuing**: Manages message buffers while simulating the resulting increase in Tower attention.
3. **Fragmentation Logic**: Resolves how hubs degrade under extreme pressure, transitioning to states like `PARTIALLY_OFFLINE` to protect the underlying network.

## Terminal Integration
Admins can monitor the status of relay hubs through the `relay status` and `relay audit` commands in the Restricted Admin Terminal. This provides visibility into hub stability, message traffic, and fragmentation history.

## Conclusion
The Tower Relay Node system provides a lore-compatible and technically secure path for survivor interaction. It ensures that the network is as hostile and fragile as the Tower itself, while strictly protecting player persistence and the decentralized nature of the engine.
