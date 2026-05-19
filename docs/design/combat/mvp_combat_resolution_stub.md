# MVP Combat Resolution Stub

## Overview
The MVP Combat Resolution Stub provides a deterministic, non-real-time mechanism for resolving combat encounters. It acts as a bridge between bounded combat session data and the project's existing MVP outcome pipeline.

## Deterministic Resolution
Combat outcomes are decided based on a set of logical rules applied to the `CombatSession` state. This avoids the complexity of real-time simulation while still allowing for strategic depth through resource management and build optimization.

### Resolution Rules
- **DEFEAT_DROP**: Triggered if player health reaches zero, or if enemy pressure is overwhelming (>= 0.90) and player health is critically low (< 25).
- **RETREAT_TO_HUB**: Triggered if resource depletion is too high (e.g., >= 25 potions used) and enemy pressure is significant (> 0.60).
- **VICTORY_ASCEND**: Triggered if the player maintains positive health and enemy pressure remains within manageable bounds (<= 0.75).

## Pipeline Integration
The resolution stub does not bypass the core project loops. Once an outcome is determined, it is fed directly into the `mvp_outcome_pipeline`.

- **Victory**: Increases floor count and records victory residue.
- **Defeat**: Triggers floor mutation, attaches survivor marks, and records defeat residue.
- **Retreat**: Safely exits the floor without mutation.

## Bounded Constraints
- **Non-Real-Time**: All resolution happens in a single logical step.
- **No AI/Physics**: Enemy behavior is abstracted into the `enemy_pressure_rating`.
- **Stat-Driven**: Player performance is modeled through health, damage, defense, and resource consumption.

## Future Extensibility
While currently a stub, the `CombatSession` schema is designed to accommodate more granular "tick-based" resolution in future iterations without breaking the existing pipeline integration.
