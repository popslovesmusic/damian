# MVP Enemy Archetype Boundary

## Overview
The MVP Enemy Archetype Boundary defines the logical framework for enemies as sources of **combat pressure** within Project Damian. It establishes archetypes and their roles without implementing actual enemy AI, runtime behavior, or visual representation.

## Enemies as Pressure Inputs
In this phase, enemies are treated as data-driven inputs that feed the combat resolution pipeline. They represent different types of challenges that the player must overcome through strategy and resource management.

### Core Archetypes
- **Pressure Unit**: Tests baseline survivability through direct damage and positioning pressure.
- **Ambush Unit**: Punishes repetitive movement habits and careless routing.
- **Attrition Unit**: Drains player resources (potions, items) over time to pressure farming loops.
- **Counter Unit**: Manifests through residue adaptation to counter dominant player strategies.

## Bounded Design Principles
To maintain project integrity and prevent scope creep, enemy archetypes are strictly bounded:
- **No Unavoidable Defeat**: No enemy archetype is allowed to grant an unavoidable defeat status to the player.
- **No God-Mode Requirement**: No enemy should require "god-mode" (infinite stats or invulnerability) to defeat.
- **Pipeline Compliance**: All enemy pressure must be processed through the existing combat resolution pipeline.

## Residue Adaptation
Enemy archetypes are designed to support **Residue Adaptation**. As the player leaves residue behind (through repeated strategies or deaths), the tower may bias the selection of specific enemy archetypes (like the `counter_unit`) to increase the pressure on those specific strategies.

## Out of Scope
The following systems are explicitly **OUT OF SCOPE** for this boundary:
- Real-time AI behavior trees or pathfinding.
- Spawning logic and map placement.
- Animation and visual rendering.
- Real-time physics or collision simulation.
- GPU-accelerated combat or logic.
