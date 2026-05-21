# Enemy Ecology, Procedural Behavior, and Pressure AI

## Overview
Stage 058 transforms hostile entities from static monsters into procedural ecological pressures. In the Tower, enemies are not just combat targets; they are adaptive responses to survivor activity, route usage, and systemic instability. This system ensures that the world's hostility feels alive, reactive, and deeply tied to the player's choices and the Tower's shifting state.

## Enemy Ecology Boundary
The `engine/enemies/contracts/enemy_ecology_boundary.json` defines the strict safety rules for procedural behavior:
- **Readable and Bounded**: Enemy adaptation (e.g., aggression, speed) must remain within defined bounds to ensure combat remains fair and readable.
- **Pressure-Reactive**: Enemies dynamically adapt to the world's current pressure level, with high pressure triggering mutations and heightened aggression.
- **Ecological Migration**: Predator density and migration patterns shift based on route usage, penalizing overused paths and encouraging strategic traversal.
- **Threat Readability**: Even under extreme pressure or mutation, threat telegraphs and behavior patterns must remain recognizable and avoidable through skilled play.

## Enemy Behavior Contract
The behavior contract (`engine/enemies/contracts/enemy_behavior_contract.json`) specifies the required state for an enemy profile:
1. **Ecology Types**: Categorizes entities into roles like `SCAVENGER`, `PREDATOR`, `RECLAMATION_HUNTER`, or `EVENT_MUTANT`.
2. **Adaptation Profiles**: Tracks how an individual profile has mutated or scaled in response to systemic pressure.
3. **Migration and Hunt Logic**: Defines how the entity responds to noise, route activity, and survivor presence.
4. **Telegraphing**: Ensures that all attacks have auditable warning windows and cues.

## Enemy Ecology Manager
The `engine/enemies/runtime/enemy_ecology_manager.py` component manages the entity lifecycle:
1. **Profile Generation**: Produces hash-verified enemy profiles that adapt to world pressure and route usage.
2. **Predator Migration**: Calculates how ecological shifts occur in response to player navigation patterns.
3. **Readability Validation**: Audits enemy telegraphs to ensure they remain within the mandatory safety windows.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `enemy status` and `enemy audit` commands to monitor active ecological configurations and review the history of procedural adaptation.
- **Dashboard**: The player dashboard displays hints of "Ecological Shift" and the current "Predator Density" in their active region.

## Conclusion
The Enemy Ecology system ensures that Damian's hostility is as procedural and dynamic as its world generation. It creates a living, reactive environment where survivors must constantly adapt to the ever-shifting pressures of the Tower's inhabitants.
