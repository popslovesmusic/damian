# Tower Engine Operational Economy and Resource Drain Architecture

This document defines the economic model for the Tower Engine, designed to create a sense of abundant loot while simultaneously ensuring continuous resource drain through operational costs. The goal is to establish strategic pressure points that prevent runaway accumulation of wealth and maintain a dynamic, challenging economy.

## Core Principles

*   **Abundant Surface Loot:** Players should experience frequent and visible rewards, making loot acquisition feel satisfying and plentiful. This drives engagement and provides immediate gratification.
*   **Continuous Resource Drain:** Despite visible abundance, continuous operational costs for progression, survival, domain maintenance, and strategic influence create a persistent economic pressure. This prevents players from stockpiling resources indefinitely.
*   **Strategic, Not Punitive Costs:** Costs are designed to be strategic, forcing players to make meaningful choices about resource allocation and trade-offs, rather than feeling like arbitrary punishment.
*   **Wealth Does Not Remove Risk:** Accumulation of wealth should enhance strategic options and survivability, but never entirely eliminate the inherent risks of the Tower or its adaptive challenges.
*   **Domain Upkeep Scales:** Maintenance costs for player-owned domains scale with the advantages derived from those domains, reinforcing the risk-equals-advantage principle.
*   **No Single Resource Dominance:** The economy is designed with multiple distinct resource types, each with specific roles, to prevent any single resource from becoming a universal solution.

## Economy Resource Registry (`economy_resource_registry.json`)

This registry declares the canonical currency and resource classes within the Tower Engine, along with their strategic roles.

### Economy Principle:

*   "The player may receive large visible loot amounts, but progression, survival, domain maintenance, and strategic influence continuously drain resources."

### Resource Classes:

*   **`gold`**:
    *   *Role*: `liquid_currency`.
    *   *Description*: Common high-volume currency for basic needs (potions, repairs, travel, crafting) and maintenance.
*   **`domain_essence`**:
    *   *Role*: `domain_influence_currency`.
    *   *Description*: Resource spent to adjust conquered home-domain parameters.
*   **`stability_shards`**:
    *   *Role*: `stability_resource`.
    *   *Description*: Used to suppress dangerous mutations, reinforce anchors, and maintain domain coherence.
*   **`residue_fragments`**:
    *   *Role*: `mutation_resource`.
    *   *Description*: Used to bias mutations, reveal hidden marks, or interact with replay-floor memory.
*   **`rare_materials`**:
    *   *Role*: `strategic_upgrade_resource`.
    *   *Description*: Lower-frequency materials for gear upgrades, relic crafting, and high-value dashboard actions.

### Global Rules:

*   `large_loot_numbers_allowed`
*   `small_unit_costs_allowed`
*   `aggregate_use_creates_pressure`
*   `upkeep_scales_with_domain_advantage`
*   `wealth_does_not_cancel_residue`
*   `wealth_does_not_cancel_death_consequence`
*   `no_single_resource_solves_all_systems`

## Operational Cost Profile Contract (`operational_cost_profile.schema.json`)

This JSON Schema validates a player's or domain's operational cost profile, illustrating how continuous resource drain is tracked.

### Key Fields:

*   `profile_id`, `player_id`, `content_pack_id`: Unique identifiers.
*   `surface_loot_recent`: An object detailing recent loot acquisition (`gold_collected`, `items_collected`, `rare_materials_collected`). All values must be non-negative.
*   `recurring_costs`: An object breaking down ongoing expenses (`potions`, `repairs`, `travel`, `crafting`, `domain_maintenance`, `mutation_control`, `hazard_upkeep`, `invasion_preparation`). All costs must be non-negative.
*   `pressure_indicators`: An object providing insights into economic pressure (`net_gold_after_costs`, `maintenance_ratio`, `farming_needed`, `risk_removed_by_wealth`). Crucially, `risk_removed_by_wealth` must always be `false`.

## Example Operational Cost Profile (`example_operational_cost_profile.json`)

This file provides a concrete example profile, demonstrating a player with `10000` gold collected recently, but also a range of recurring costs. The `net_gold_after_costs` shows the impact of the drain, and `farming_needed` is `true`, while `risk_removed_by_wealth` is `false`, aligning with the core principles.

## Validation and Integrity

The validation script (`tests/validate_operational_economy.py`) ensures:
*   The `economy_resource_registry.json` exists and declares at least 5 resource classes and required global rules.
*   The `operational_cost_profile.schema.json` is a valid JSON Schema.
*   The `example_operational_cost_profile.json` validates successfully against the schema.
*   The example includes `gold_collected = 10000`.
*   The example shows a potion or similar cost that appears small relative to the loot collected, reinforcing the "small unit costs" rule.
*   `farming_needed` is `true` and `risk_removed_by_wealth` is `false` in the example.
