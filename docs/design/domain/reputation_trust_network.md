# Survivor Reputation and Residue Trust Network

## Overview
Stage 042 establishes the social trust and reputation layer for the Tower ecosystem. This system tracks the "residue" of survivor actions—cooperation, treaties, attacks, and support—to generate persistent but recoverable reputation signals. It is designed to foster strategic trust without enabling permanent social exile or live social scoring.

## Reputation Boundary
The `engine/domain/contracts/reputation_boundary.json` defines the strict safety rules:
- **No Global Social Credit**: Reputation is contextual and limited to the Tower ecosystem.
- **Recoverability**: No negative signal results in permanent, irreversible punishment. All trust can be rebuilt through positive actions.
- **No OS Control**: Reputation never grants or revokes OS-level administrative authority.
- **Bounded Retaliation**: Retaliation traces are limited in duration and scope to prevent infinite feedback loops of hostility.

## Trust Network Contract
The trust network (`engine/domain/contracts/trust_network_contract.json`) specifies the required fields for a survivor's reputation snapshot:
1. **Residue Score**: A numerical representation of a survivor's general reliability.
2. **Treaty Trust**: Specifically tracks performance and reliability within formed treaties.
3. **Drift State**: Categorizes the current reputation (e.g., `RELIABLE`, `UNSTABLE`, `RECOVERING`).
4. **Recovery Potential**: Tracks how much "memory" remains for trust to be restored.

## Reputation Manager
The `engine/domain/reputation_manager.py` component manages the trust lifecycle:
1. **Signal Generation**: Translates survivor actions (like successful joint defense or treaty abandonment) into bounded reputation signals.
2. **Trust Drift**: Calculates the evolution of a survivor's score over time, incorporating decay and new evidence.
3. **Snapshot Generation**: Produces hash-verified, contextual reports for display in the dashboard and terminal.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `reputation status` and `reputation audit` commands to review trust network state and signal history.
- **Dashboard**: The player dashboard displays a partial, lore-compatible view of their own reputation and the "noise" their actions have left in the Tower.

## Conclusion
The Survivor Reputation and Residue Trust Network provides a meaningful social dimension to the Tower. It ensures that actions have lasting consequences while strictly protecting the player's ability to recover and the system's foundational safety boundaries.
