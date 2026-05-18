# Tower Engine Home Domain and Conquest Architecture

This document defines the architectural patterns and contractual agreements for player-owned "Home Domains" and the associated "Conquest" mechanics within the Tower Engine. This system aims to provide players with a persistent strategic layer, allowing them to influence portions of the Tower they've claimed, while ensuring a balanced risk-reward economy and preventing runaway power.

## Core Principles

*   **Content Pack Driven Home Domains:** The fundamental archetypes and initial conditions for home domains are defined by content packs, allowing for themed and unique player bases.
*   **Conquest as Unlock:** Home domains are not given; they are conquered through gameplay, unlocking dashboard functionality.
*   **Bounded Domain Influence:** Player modifications to their domain (via the dashboard) are always bounded. No action can create an unplayable, uninvadable, or unchallenging domain.
*   **Risk Equals Advantage:** Every advantage gained through domain influence must be offset by an equal or greater cost or risk. There is no "free lunch."
*   **Owner Not Immune:** The domain owner is never immune to the effects and challenges within their own domain. They face the same, or potentially enhanced, risks as invaders.
*   **Economic Pressure:** Domain maintenance and modification incur operational costs, creating a strategic tension between desired advantages and resource management. This pressure is designed to be operational, not punitive.

## Home Domain Registry (`home_domain_registry.json`)

This registry declares the canonical archetypes for player-owned home domains and their inherent characteristics.

### Domain Archetypes:

*   **`tower_domain`**:
    *   *Theme*: Vertical recursion and adaptive floors.
    *   *Example Owner*: Damian.
    *   *Core Risks*: `instability_growth`, `recursive_enemy_adaptation`.
*   **`swamp_domain`**:
    *   *Theme*: Concealment, decay, poison ecology.
    *   *Example Owner*: Jacob.
    *   *Core Risks*: `visibility_loss`, `terrain_attrition`.
*   **`castle_domain`**:
    *   *Theme*: Fortification, halls, siege memory.
    *   *Example Owner*: James.
    *   *Core Risks*: `predictable_routes`, `siege_pressure`.

### Global Rules:

*   `home_domain_must_be_conquered_before_dashboard_unlock`
*   `all_dashboard_changes_require_cost`
*   `all_advantages_require_equal_or_greater_risk`
*   `domain_owner_not_immune_to_domain_effects`
*   `domains_must_remain_invadable`
*   `domains_must_remain_playable`
*   `no_impossible_domains`

## Domain State Contract (`domain_state.schema.json`)

This JSON Schema validates the persistent state of a player's owned domain.

### Key Fields:

*   `domain_state_id`, `owner_player_id`, `content_pack_id`, `domain_archetype`: Core identifiers.
*   `conquered`, `dashboard_unlocked`: Status flags.
*   `domain_level`: The current progression level of the domain.
*   `stability`, `deviation`: Metrics influencing the domain's dynamic properties (0.0-1.0).
*   `active_modifiers`: List of active effects applied to the domain.
*   `operational_costs`: An object detailing ongoing resource drains (`maintenance`, `mutation_control`, `hazard_upkeep`, `resource_transport`). All costs must be non-negative.
*   `invasion_history`: Records past invasion attempts.
*   `forbidden_flags`: Boolean flags (`playability_failure`, `owner_immunity`, `impossible_layout`) that must *always* be `false` to ensure domain integrity.

## Domain Dashboard Action Contract (`domain_dashboard_action.schema.json`)

This JSON Schema validates actions performed by a player through their domain dashboard to modify their domain. It enforces the risk-equals-advantage principle.

### Key Fields:

*   `action_id`: Unique identifier for the action.
*   `parameter_modified`: The specific domain characteristic being altered.
*   `advantage_gained`: Description of the strategic benefit.
*   `risk_incurred`: Description of the strategic drawback or increased challenge.
*   `resource_cost`, `stability_cost`: Quantifiable costs associated with the action (non-negative).
*   `playability_preserved`: Must always be `true`. Actions cannot make the domain unplayable.
*   `owner_affected`: True if the owner also faces the consequences of the action.

## Example Domain State (`example_domain_state.json`)

This file provides a concrete example of a valid `domain_state`, demonstrating a conquered `tower_domain` owned by `player_damian_001`, with active modifiers, defined operational costs, and all `forbidden_flags` set to `false`.

## Validation and Integrity

The validation script (`tests/validate_home_domain_architecture.py`) ensures:
*   The `home_domain_registry.json` exists and declares at least 3 archetypes and required global rules.
*   Both `domain_state.schema.json` and `domain_dashboard_action.schema.json` are valid JSON Schemas.
*   The `example_domain_state.json` validates successfully against its schema.
*   `operational_costs` in the example are non-negative.
*   All `forbidden_flags` in the example `domain_state` are `false`.
*   The `domain_dashboard_action_contract` implicitly enforces the "advantage gained / risk incurred" balance.
*   The conceptual rule that "Progression language emphasizes survivability rather than supremacy" is acknowledged as a design principle.
