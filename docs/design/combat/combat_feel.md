# Combat Feel, Animation, and Procedural Feedback Runtime

## Overview
Stage 056 transforms the core combat pressure systems into a readable and satisfying player-facing experience. In the Tower, combat is not just a calculation; it is a violent and consequential event. This system uses animation timing, hitstop duration, screen effects, and procedural audio to communicate the "weight" of every hit and the severity of systemic pressure.

## Combat Feel Boundary
The `engine/combat/contracts/combat_feel_boundary.json` establishes the strict rules for player-facing feedback:
- **Readability First**: Visual effects and animations must never obscure the game state or hide enemy threats.
- **Pressure-Reactive**: Hit feedback (hitstop duration, vignette intensity) scales dynamically with the survivor's current environmental and systemic pressure.
- **Legacy Support**: Effects are designed to be procedural and low-cost, ensuring they scale down cleanly for legacy hardware without losing gameplay clarity.
- **Consequential**: Every hitstop and screen shake is a direct communication of impact and risk, rather than a generic "juice" effect.

## Combat Feedback Contract
The feedback contract (`engine/combat/contracts/combat_feedback_contract.json`) specifies the required state for a hit profile:
1. **Damage Bands**: Categorizes hits into `LIGHT`, `MEDIUM`, `HEAVY`, or `CRITICAL` to provide visual and auditory distinction.
2. **Hitstop Profile**: Defines the momentary "freeze" on impact, which scales with damage and pressure to provide tactile weight.
3. **Screen Feedback**: Manages color tints, vignettes, and camera shakes that reflect the severity of the hit and the survivor's instability.
4. **Telegraphing**: Ensures that enemy attacks have recognizable warning windows that preserve player agency and readability.

## Combat Feel Manager
The `engine/combat/runtime/combat_feel_manager.py` component manages the feedback lifecycle:
1. **Feedback Generation**: Produces hash-verified feedback profiles based on hit data and systemic context.
2. **Timing Calculation**: Resolves hitstop durations that provide a satisfying "crunch" while adhering to performance limits.
3. **Threat Validation**: Gathers evidence that enemy telegraphs remain within readable and survivable bounds.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `combat status` and `combat audit` commands to review active feedback configurations and verify hitstop timing audits.
- **Dashboard**: The player dashboard displays evidence of "Combat Stress" and the visual indicators associated with different damage bands.

## Conclusion
The Combat Feel system ensures that Damian's combat is violent, readable, and deeply tied to its core pressure mechanics. It creates a visceral loop where survivors feel the weight of their choices and the hostility of the Tower in every impact.
