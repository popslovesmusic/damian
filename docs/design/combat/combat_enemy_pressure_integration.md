# Combat Enemy Pressure Integration

## Overview
Project Damian's combat resolution system has been updated to integrate **Enemy Pressure Profiles**. This integration allows deterministic enemy archetypes (like the `attrition_unit` or `counter_unit`) to influence the outcome of combat encounters without requiring real-time simulation or AI.

## Archetype Influence
Enemy archetypes provide a structured way to bias the combat resolution stub:

### Pressure Unit
- **Baseline**: Represents the standard combat difficulty for the floor.
- **Influence**: Maintains the base pressure rating derived from mutation levels.

### Ambush Unit
- **Lethality**: Punishes low-health players more severely.
- **Influence**: Increases the effective pressure rating if player health falls below a critical threshold (e.g., 40%), significantly raising the risk of a `DEFEAT_DROP`.

### Attrition Unit
- **Resource Drain**: Simulates long-term resource depletion.
- **Influence**: Automatically flags `resource_pressure_observed` as true, signaling the tower that the player is being forced to consume excessive resources (potions, etc.).

### Counter Unit
- **Strategic Adaptation**: Represents the tower's response to overused player tactics.
- **Influence**: Automatically flags `residue_pressure_observed` as true, feeding back into the residue system to further refine tower adaptations.

## Bounded Resolution
The integration strictly adheres to the project's deterministic and bounded rules:
1. **Pipeline Compliance**: All combat outcomes must still be resolved through the `mvp_outcome_pipeline`.
2. **Deterministic Outputs**: For any given set of inputs (archetype, health, resources), the resolution is always identical.
3. **Non-Playable Boundary**: No real-time AI, spawning, or physics are introduced. Resolution is purely data-driven.

## Data Flow
1. **Selector**: Chooses an enemy archetype based on floor residue and mutation.
2. **Profile Builder**: Constructs a bounded pressure profile.
3. **Combat Session**: `make_combat_session` incorporates the profile.
4. **Resolution**: `resolve_combat_session` applies archetype-specific biases.
5. **Outcome**: Results in `VICTORY_ASCEND`, `DEFEAT_DROP`, or `RETREAT_TO_HUB`.
