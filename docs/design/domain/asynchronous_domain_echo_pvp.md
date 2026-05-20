# Asynchronous Domain Echo PvP Boundary

## Overview
Stage 039 defines the boundary for asynchronous adversarial play in Damian. This system uses "Domain Echoes"—verifiable, hostile-readable snapshots of a player's Tower state—that can be attacked by other players offline. This allows for competitive pressure without requiring live multiplayer or destructive griefing.

## Domain Echoes
A Domain Echo is a read-only shadow of a player's domain.
- **Exporting**: Players can publish a `DomainEcho` snapshot (governed by `engine/domain/contracts/domain_echo_snapshot_contract.json`) which summarizes their claims, routes, residues, and defense profiles.
- **Verification**: All exported echoes are hash-verified to ensure they represent a valid state of the Tower.
- **Privacy**: Only lore-compatible summaries and combat-relevant data are exported; internal OS state and host secrets are never included.

## Offline Attack Resolution
Hostile players can import a `DomainEcho` and attempt an attack.
- **Resolution**: Attacks are resolved asynchronously using `engine/domain/offline_attack_resolver.py` according to the `offline_attack_resolution_boundary.json`.
- **Bounded Outcomes**: Results are limited to "pressure spikes," "reclamation increases," or "domain scarring." Permanent deletion or save wiping is strictly forbidden.
- **Delayed Consequences**: The owner of the domain receives a `DelayedConsequenceReport` upon their next boot, allowing them to recover or retaliate.

## Anti-Griefing and Safety
- **No Live Mutation**: Attackers can never modify the owner's active save file directly.
- **Recoverability**: All consequences applied via an echo attack are designed to be recoverable through standard Tower gameplay (residue cleaning, repair).
- **Auditability**: Every attack is logged and verifiable by both parties, preventing "ghost attacks" or unidentifiable griefing.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `echo export` and `echo report` commands to manage and review adversarial state.
- **Console Transcripts**: Attacks against an echo generate defense transcripts, allowing players to replay how their domain defended itself.

## Conclusion
The Asynchronous Domain Echo system provides a safe and lore-compatible path for adversarial play. it ensures that the Tower remains a hostile and competitive environment while strictly protecting the player's continuity and the system's integrity.
