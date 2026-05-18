# Tower Engine Domain Dashboard Parameter Influence Contract

This document defines the contractual agreements and design philosophy for post-conquest "Domain Dashboard" controls within the Tower Engine. These controls allow players to influence the procedural generation parameters of their owned home domains at a bounded cost and risk, maintaining the game's core risk-equals-advantage dynamic.

## Core Principles

*   **Post-Conquest Unlock:** The Domain Dashboard and its controls are only accessible after a player has successfully conquered their home domain, tying strategic influence to gameplay achievement.
*   **Cost for Every Change:** Every modification made through the dashboard, regardless of its perceived benefit, must incur a tangible cost (resources, stability, etc.). There are no "free" adjustments.
*   **Risk-Equals-Advantage:** Any advantage gained by altering domain parameters must be balanced by an equal or greater corresponding risk, cost, or exposure. This prevents players from creating invincible or unchallenged domains.
*   **Owner Affected by Changes:** The domain owner is not immune to the effects of their own dashboard modifications. If a change increases hazard density, the owner also faces that increased hazard density.
*   **No Positive-Only Upgrades:** There are no upgrades that provide only benefits without any associated drawbacks. Every choice carries a strategic trade-off.
*   **Playability Guaranteed:** All dashboard changes must respect the engine's core playability constraints. It should be impossible to use the dashboard to create an unplayable or soft-locked domain.

## Domain Dashboard Parameter Registry (`domain_dashboard_parameter_registry.json`)

This registry declares the allowed domain dashboard parameters that players can influence, along with their associated benefits and mandatory risks.

### Unlock Rule:

*   "dashboard_unlocked only after home_domain conquered = true" - Reinforces the acquisition requirement.

### Core Principle:

*   "Dashboard changes influence generation but never grant free advantage; every benefit must create cost, exposure, instability, maintenance, or counterplay."

### Parameters:

*   **`enemy_density_bias`**:
    *   *Benefit*: Increases defender pressure and potential loot density.
    *   *Required Risks*: `higher_domain_upkeep`, `owner_faces_same_density`, `increased_residue_visibility`.
*   **`hazard_bias`**:
    *   *Benefit*: Increases environmental pressure against invaders.
    *   *Required Risks*: `owner_affected_by_hazards`, `higher_stability_cost`, `possible_route_fragility`.
*   **`loot_cache_bias`**:
    *   *Benefit*: Increases chance of hidden caches and rare rewards.
    *   *Required Risks*: `higher_invasion_visibility`, `stronger_elite_attention`, `increased_mutation_pressure`.
*   **`secret_frequency_bias`**:
    *   *Benefit*: Increases hidden survivor mark and secret event opportunities.
    *   *Required Risks*: `higher_discoverability_by_invaders`, `higher_memory_fragment_cost`, `secret_mutation_if_unclaimed`.
*   **`boss_behavior_bias`**:
    *   *Benefit*: Influences boss tendencies toward aggression, defense, summons, traps, or mobility.
    *   *Required Risks*: `boss_unpredictability`, `owner_training_cost`, `higher_failed_defense_residue`.
*   **`route_complexity_bias`**:
    *   *Benefit*: Makes domain navigation less direct.
    *   *Required Risks*: `owner_navigation_cost`, `must_preserve_primary_route`, `higher_softlock_validation_cost`.

### Forbidden Dashboard Results:

These outcomes are strictly prohibited for any dashboard action:

*   `free_advantage`
*   `owner_immunity`
*   `invader_softlock`
*   `unreachable_domain_core`
*   `guaranteed_defense`
*   `guaranteed_reward`
*   `riskless_loot_increase`
*   `positive_only_upgrade`

## Domain Parameter Change Contract (`domain_parameter_change.schema.json`)

This JSON Schema validates a player's request to modify a domain parameter through the dashboard. It formalizes the costs, benefits, and risks associated with such actions.

### Key Fields:

*   `change_id`, `domain_state_id`, `owner_player_id`, `parameter_id`: Identifiers for the change and associated entities.
*   `requested_delta`: The quantitative change being applied to the parameter.
*   `benefit_declared`: A textual description of the expected positive outcome.
*   `costs_paid`: An object detailing the specific resource costs (gold, domain essence, etc.) to enact the change. All values must be non-negative.
*   `risks_incurred`: An array of strings describing the drawbacks or increased challenges resulting from the change. Must include at least one risk.
*   `owner_affected`: Must be `true`. The owner always faces consequences.
*   `playability_preserved`, `primary_route_preserved`, `risk_advantage_equilibrium_preserved`: Must all be `true`, ensuring fundamental integrity.
*   `forbidden_flags`: An object of boolean flags (`free_advantage`, `owner_immunity`, `positive_only_upgrade`, `softlock_risk`) that must *always* be `false` to prevent exploits.

## Example Domain Parameter Change (`example_domain_parameter_change.json`)

This file provides a concrete example of a valid dashboard action: an owner increasing `enemy_density_bias`. It details the paid costs, the declared benefit, and the explicitly incurred risks, demonstrating compliance with the `owner_affected`, `playability_preserved`, `primary_route_preserved`, and `risk_advantage_equilibrium_preserved` rules, and with all `forbidden_flags` set to `false`.

## Validation and Integrity

The validation script (`tests/validate_domain_dashboard_parameters.py`) ensures:
*   The `domain_dashboard_parameter_registry.json` exists, declares at least 6 parameters, and each parameter has a benefit and non-empty `required_risks`.
*   The `domain_parameter_change.schema.json` is a valid JSON Schema.
*   The `example_domain_parameter_change.json` validates successfully against the schema.
*   The example explicitly sets `owner_affected`, `playability_preserved`, `primary_route_preserved`, and `risk_advantage_equilibrium_preserved` to `true`.
*   All `forbidden_flags` in the example are `false`.
