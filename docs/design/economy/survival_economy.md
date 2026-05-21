# Resource Scarcity, Crafting Pressure, and Survival Economy Runtime

## Overview
Stage 059 transforms resources and crafting into pressure-driven survival systems. In the Tower, resources are never permanent loot; they are temporary procedural leverage against systemic collapse. This system ensures that scarcity, decay, and the burden of repair shape every decision the survivor makes.

## Resource Scarcity Boundary
The `engine/economy/contracts/resource_scarcity_boundary.json` defines the strict safety rules:
- **Resources Must Remain Scarce**: Infinite resource generation is prohibited.
- **Decay and Perishability**: Critical resources (food, water, medical supplies) decay over time, with the rate increasing under high systemic pressure.
- **Inventory Weight**: Carrying resources is a physical burden. Weight affects traversal drag, exhaustion rates, and the ability to escape hostile encounters.
- **Visibility Coupling**: Hoarding high-value resources increases a survivor's visibility to the Tower, attracting scavengers and predators.

## Survival Economy Contract
The economy contract (`engine/economy/contracts/survival_economy_contract.json`) specifies the required state for a resource profile:
1. **Scarcity and Density**: Defines regional availability and the resulting market value.
2. **Decay Profile**: Tracks the lifespan of an item and its vulnerability to environmental instability.
3. **Repair and Crafting Cost**: Models the meaningful burden of maintaining tools and equipment.
4. **Cache Risk**: Defines the vulnerability of stored resources to discovery and theft.

## Survival Economy Manager
The `engine/economy/runtime/survival_economy_manager.py` component manages the resource lifecycle:
1. **Profile Generation**: Produces hash-verified, pressure-reactive resource profiles.
2. **Scavenging Pressure**: Calculates the risks and rewards of searching for supplies, ensuring that longer scavenging sessions increase exposure risk.
3. **Improvised Crafting**: Simulates crafting under pressure, where quality is inversely proportional to systemic instability, leading to imperfect but viable survival tools.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `economy status` and `economy audit` commands to monitor resource distribution and review the history of crafting pressure.
- **Dashboard**: The player dashboard displays evidence of "Supply Scarcity," "Perishable Risk," and the "Inventory Burden" currently affecting their survival chances.

## Conclusion
The Survival Economy system ensures that Damian remains a game of strategic choice and constant pressure. It reinforces the engine's core identity by making every resource find and crafting decision a critical step in the survivor's journey.
