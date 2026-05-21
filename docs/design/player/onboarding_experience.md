# Player Onboarding, Tutorialization, and First-Hour Experience

## Overview
Stage 061 defines the onboarding and first-hour experience for Damian. The primary goal is to teach the core survival loop—pressure, traversal, combat, social layers, and recoverability—naturally through gameplay. Damian avoids "theme-park" tutorialization, instead favoring contextual, environmental learning that preserves the Tower's hostile identity while ensuring survivors reach meaningful agency quickly.

## Onboarding Boundary
The `engine/player/contracts/first_hour_boundary.json` defines the strict safety rules:
- **No Static Tutorials**: Forced, lengthy text dumps and information overloads are prohibited.
- **Contextual Learning**: All teaching must be tied to the current environment and systemic pressure.
- **Fail-Safe Onboarding**: The first failure is treated as a teaching moment for recoverability, rather than a punitive reset.
- **Progressive Reveal**: The player dashboard and systemic complexities are revealed incrementally to manage cognitive load.

## Onboarding Flow Contract
The flow contract (`engine/player/contracts/onboarding_contract.json`) specifies the required topics and milestones:
1. **Entry Sequence**: Communicates the Tower's identity and the survivor's descent.
2. **Core Mechanics**: Incremental teaching of movement, combat, and resource management through pressure-based scenarios.
3. **Ecosystem Exposure**: Introduction to treaties, relay hubs, and Domain Echoes as natural extensions of survival coordination.
4. **Recovery Run**: A mandatory (but guided) demonstration of how the survivor's identity and residue survive defeat.

## Onboarding Manager
The `engine/player/runtime/onboarding_manager.py` component manages the first-hour UX:
1. **Profile Generation**: Produces a hash-verified onboarding profile that tracks a survivor's learning milestones.
2. **Advancement Logic**: Updates teaching states (e.g., from "Contextual Hints" to "Active Feedback") based on player actions.
3. **UX Smoke Testing**: Simulates the complete first-hour journey to ensure engagement, clarity, and the auditable nature of the player's lineage.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `onboarding status` and `onboarding audit` commands to monitor learner progress and review first-hour UX evidence.
- **Dashboard**: The player dashboard progressively unlocks layers (Health -> Pressure -> Residue -> Social) as milestones are reached, ensuring clarity under load.

## Conclusion
The Onboarding system ensures that Damian provides a compelling and atmospheric entry into its hostile world. It fosters survivor agency and strategic understanding through immersive gameplay, reinforcing the engine's core identity of persistent survival and procedural consequence.
