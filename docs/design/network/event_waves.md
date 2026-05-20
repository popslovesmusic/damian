# Tower Event Waves and Global Procedural Pressure

## Overview
Stage 045 defines the infrastructure for large-scale asynchronous Tower pressure events. These "Event Waves" represent the Tower moving as a hostile procedural force, creating shared crises that propagate through relay nodes, treaties, and Domain Echoes without requiring real-time synchronization.

## Event Wave Boundary
The `engine/network/contracts/event_wave_boundary.json` defines the strict safety rules:
- **No Real-Time Simulation**: Event waves are asynchronous and propagate contextually across the distributed network.
- **Recoverable Scars**: While events can scar domains or echoes, these impacts must remain recoverable through standard gameplay.
- **Auditable Evidence**: Every global pressure event is hash-verified and recorded in system audit logs.
- **Probabilistic Forecasting**: Survivor warning signals are designed to be partial and probabilistic, maintaining the Tower's mystery and hostility.

## Global Pressure Contract
The pressure contract (`engine/network/contracts/global_pressure_contract.json`) specifies the required state for an event wave:
1. **Event Types**: Supported types include `RECLAMATION_WAVE`, `MUTATION_BLOOM`, and `RELAY_FRAGMENTATION`.
2. **Propagation Profile**: Defines how pressure scales across relay hubs and treaties (e.g., visibility modifiers).
3. **Impact Profile**: Specifies how Domain Echoes are affected (e.g., probability of pressure scarring).
4. **Forecast Instability**: Tracks the inherent uncertainty of the event's trajectory.

## Event Wave Manager
The `engine/network/runtime/event_wave_manager.py` component orchestrates the pressure lifecycle:
1. **Wave Generation**: Produces bounded, hash-verified event artifacts.
2. **Distributed Propagation**: Simulates how pressure spikes bleed through relay hubs based on their current attention levels.
3. **Non-Omniscient Forecasting**: Generates probabilistic warnings for survivors, avoiding "perfect" future predictions.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `event status`, `event forecast`, and `event audit` commands to monitor global pressure and its propagation history.
- **Dashboard**: The player dashboard displays evidence of impending waves and the "Forecast Uncertainty" associated with survivor signals.

## Conclusion
The Tower Event Wave system ensures that the world of Damian remains dynamic and unpredictable. It allows for massive, shared adversarial moments that respect the engine's asynchronous architecture and safety-first design principles.
