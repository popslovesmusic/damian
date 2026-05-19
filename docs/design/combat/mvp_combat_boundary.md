# MVP Combat System Boundary

## Overview
The MVP Combat System Boundary defines the logical framework for resolving combat encounters within Project MVP. It establishes the rules, constraints, and integration points for combat without implementing real-time simulation, AI, or rendering.

## Bounded Growth Philosophy
To maintain long-term game balance and progression integrity, combat is strictly governed by **Bounded Growth Rules**. These rules prevent "god modes" and ensured that player power always comes with associated costs and risks.

### Core Constraints
- **No Permanent Invulnerability**: Players must always be susceptible to damage.
- **No Infinite Scaling**: All stats (damage, health, etc.) have logical ceilings or diminishing returns.
- **Resource Upkeep**: High-power builds require increasing amounts of resources (potions, repairs) to maintain efficiency.

## Residue Pressure
Combat is not just a binary win/loss; it contributes to the global game state through **Residue Pressure**.

- **Dominant Build Visibility**: Using the same powerful build repeatedly increases its "visibility," prompting the tower systems to increase counter-pressure.
- **Strategy Repetition**: Repeating the same tactics increases residue accumulation, leading to faster floor mutations upon defeat.

## Outcome Integration
All combat encounters must terminate in one of the predefined outcomes:
- `VICTORY_ASCEND`: The player clears the encounter and advances.
- `DEFEAT_DROP`: The player is defeated, triggering the residue and mutation pipeline.
- `RETREAT_TO_HUB`: The player chooses to exit combat safely, sacrificing progress but preserving resources.

## Scope Boundaries
The current implementation is limited to **state definitions** and **contract validation**. The following systems are explicitly **OUT OF SCOPE** for this boundary:
- Real-time physics or collision.
- Enemy AI behavior trees.
- Animation or visual effects.
- Multiplayer synchronization.
- GPU-accelerated combat calculations.
