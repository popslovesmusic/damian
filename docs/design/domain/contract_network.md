# Dynamic Quest Broadcasts and Survivor Contract Networks

## Overview
Stage 047 introduces the infrastructure for dynamic, procedural asynchronous objectives in the Tower ecosystem. This system replaces static quest boards with "Survivor Contracts" that emerge from systemic pressures, scarcity, and survivor needs, propagating through the distributed relay hub network.

## Contract Network Boundary
The `engine/domain/contracts/contract_network_boundary.json` defines the strict safety rules:
- **Asynchronous Propagation**: Contracts are broadcast through relay hubs and synchronized asynchronously.
- **Pressure Coupling**: Quest visibility is not free. Accepting or broadcast high-value contracts increases "Tower Attention" and visibility pressure.
- **Recoverable Scars**: Contract failure results in bounded consequences (reputation damage, relay instability) but never irrecoverable state loss.
- **Decay and Expiration**: Objectives are temporal and will expire if not accepted, maintaining the Tower's dynamic state.

## Quest Broadcast Contract
The quest contract (`engine/domain/contracts/quest_broadcast_contract.json`) specifies the required state for an objective:
1. **Contract Types**: Supported types include `resource_recovery`, `relay_stabilization`, and `echo_defense`.
2. **Pressure Source**: Identifies the systemic event (e.g., a supply shortage or event wave) that triggered the objective.
3. **Reward and Risk Profiles**: Balances potential gains against the increased visibility and risk of failure.
4. **Failure Scars**: Explicitly defines the negative residue left behind if the objective is not met.

## Contract Manager
The `engine/domain/contract_manager.py` component manages the objective lifecycle:
1. **Procedural Generation**: Produces hash-verified, bounded contracts based on systemic inputs.
2. **Acceptance Workflow**: Manages the survivor's commitment to an objective and the resulting visibility penalty.
3. **Failure Resolution**: Calculates the impact of failed objectives and ensures all scars are correctly bounded.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `quest status` and `quest audit` commands to monitor active objectives and review the history of contract failures.
- **Dashboard**: The player dashboard displays active broadcasts and provides visual indicators of the "Systemic Pressure" driving current objectives.

## Conclusion
The Survivor Contract Network ensures that Damian remains a living, evolving world. It fosters coordination and strategic choice through objectives that are as unpredictable and hostile as the Tower itself.
