# Tower Engine Content Module Domain Binding Contract

This document defines the contract for binding specific content modules (game titles like Damian: What Survives the Tower or Jacob's Bane) to their respective home domain archetypes, story identities, generation themes, and multiplayer conquest roles. This binding system enforces the separation of engine-level rules from content-specific implementations, ensuring that core engine principles are inherited and maintained.

## Core Principles

*   **Content Pack as Domain Identity:** Each major content pack is associated with a unique home domain that reflects its thematic and gameplay identity.
*   **Engine Rule Inheritance:** Content packs must implicitly (via this binding) and explicitly (via design documents) inherit and comply with all core engine rules, including bounded progression, risk-advantage equilibrium, playability constraints, and optional GPU boundaries.
*   **Domain Identity, Not Engine Identity:** The domain's characteristics (theme, hazards, rewards) are distinct from the engine's core rules. The content pack defines the former within the constraints of the latter.
*   **No Override of Core Rules:** Content modules may extend or specialize certain behaviors but are strictly forbidden from overriding or weakening fundamental engine-level rules.
*   **Data-Driven Customization:** Domain-specific elements like generation biases, signature hazards, and rewards are data-driven, allowing for flexible content creation within the established framework.

## Content Domain Binding Contract (`content_domain_binding.schema.json`)

This JSON Schema validates records that define the binding between a content module and its home domain.

### Key Fields:

*   `binding_id`, `content_pack_id`, `title`: Unique identifiers and display information for the content module.
*   `home_domain_id`, `home_domain_display_name`, `domain_archetype`: Identifiers for the associated home domain, which must reference a known archetype from the `home_domain_registry.json`.
*   `domain_theme`, `story_identity`: Textual descriptions capturing the thematic and narrative essence of the domain within the content pack.
*   `generation_biases`, `signature_hazards`, `signature_rewards`: Arrays of strings detailing how this content pack influences procedural generation and what unique elements it introduces.
*   `conquest_role`: An object defining the domain's behavior in multiplayer conquest scenarios, including `must_conquer_home_first`, `dashboard_unlocks_after_conquest`, `can_attack_other_domains`, and `can_be_attacked_by_other_players`.
*   `engine_rule_compliance`: An object with boolean flags (`inherits_bounded_progression`, `inherits_risk_advantage_equilibrium`, `inherits_playability_constraints`, `inherits_optional_gpu_boundary`). All these flags must be `true`, explicitly confirming compliance with core engine rules.

## Content Domain Binding Registry (`content_domain_binding_registry.json`)

This registry declares the active and planned content-domain bindings.

### Bindings:

*   **`binding_damian_tower_001`**: Binds "Damian: What Survives the Tower" to the `tower_domain` archetype.
*   **`binding_jacobs_swamp_001`**: Binds "Jacob's Bane" to the `swamp_domain` archetype.

### Global Rules:

*   `content_pack_is_not_engine`
*   `domain_binding_must_reference_known_archetype`
*   `content_may_theme_but_not_weaken_core_constraints`
*   `home_conquest_unlocks_dashboard`
*   `content_modules_are_expandable`

## Example Content Bindings (`content/damian/domain_binding.json`, `content/jacobs_bane/domain_binding.json`)

These files provide concrete examples of domain bindings for the "Damian" and "Jacob's Bane" content packs. They showcase how specific domain themes, story identities, generation biases, and conquest roles are defined within the constraints of the `content_domain_binding.schema.json`, while explicitly stating compliance with engine rules via `engine_rule_compliance` flags set to `true`.

## Validation and Integrity

The validation script (`tests/validate_content_domain_bindings.py`) ensures:
*   The `content_domain_binding.schema.json` exists and is a valid JSON Schema.
*   The `content_domain_binding_registry.json` exists and includes the Damian and Jacob's Bane bindings.
*   The `domain_binding.json` files for both Damian and Jacob's Bane exist and validate successfully against the schema.
*   The Damian binding correctly references `tower_domain`.
*   The Jacob's Bane binding correctly references `swamp_domain`.
*   Both example bindings set `must_conquer_home_first` and `dashboard_unlocks_after_conquest` to `true`.
*   All `engine_rule_compliance` flags are `true` for both examples, confirming adherence to core engine rules.
*   Conceptual check that "Neither binding redefines engine core rules" is satisfied by the `const: true` in the schema for `engine_rule_compliance` flags.
