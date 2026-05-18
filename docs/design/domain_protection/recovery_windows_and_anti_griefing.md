# Tower Engine Domain Recovery, Protection Windows, and Anti-Griefing Rules

This document defines the rules and contractual agreements for domain recovery after invasion events, temporary protection windows, and robust anti-griefing mechanisms within the Tower Engine. The goal is to ensure a fair and enjoyable multiplayer experience where domain ownership is strategic and impactful, but never leads to permanent loss or abusive behavior.

## Core Principles

*   **Conquered Domains Remain Recoverable:** Regardless of how severely a domain is impacted by an invasion, it must always remain recoverable by its owner. Permanent domain theft is strictly prohibited.
*   **Temporary Protection Windows:** Following significant events (e.g., successful invasion, heavy damage), domains enter temporary protection windows during which they cannot be re-invaded, allowing the owner to recover.
*   **Anti-Griefing Measures:** Specific rules are in place to prevent abusive behavior, such as repeated attacks from the same player/party without escalating costs, or targeting inactive players.
*   **Protection is Not Permanent Immunity:** Protection windows are temporary. They serve to facilitate recovery and strategic planning, not to grant permanent immunity from invasions.
*   **Strategic Invasion Remains Viable:** While anti-griefing is paramount, the system must not eliminate the strategic viability and impact of successful domain invasions.
*   **Offline/Low-Activity Player Protection:** Domains belonging to players who are offline or have low activity should have specific protection rules to prevent them from being perpetually targeted.

## Domain Protection Registry (`domain_protection_registry.json`)

This registry declares the canonical protection states, anti-griefing rules, and recovery rules for player-owned domains.

### Protection States:

*   **`NONE`**: Domain is fully open to normal attack rules.
*   **`RECOVERY_WINDOW`**: A temporary state triggered after a major invasion outcome (e.g., successful conquest or heavy damage), preventing further immediate invasions.
*   **`LOW_ACTIVITY_SHIELD`**: Applies to inactive or low-activity players, reducing their exposure to invasion pressure.
*   **`FAILED_SAFE_LOCK`**: A temporary lock imposed after critical validation failures, exploit detection, or attempts to create impossible domain states, allowing for system intervention.
*   **`COOLDOWN_AFTER_REPEAT_ATTACK`**: A temporary restriction imposed on attackers after repeatedly targeting the same domain within a short period.

### Anti-Griefing Rules:

*   `same_attacker_repeat_invasions_require_escalating_cost`
*   `failed_safe_sessions_do_not_award_full_conquest`
*   `offline_players_may_receive_reduced_invasion_exposure`
*   `domain_damage_cannot_stack_to_permanent_unrecoverability`
*   `protection_windows_expire`
*   `protection_windows_do_not_grant_permanent_immunity`
*   `strategic_invasions_remain_allowed_after_recovery`

### Recovery Rules:

*   `domain_recovery_restores_playability_before_next_valid_invasion`
*   `owner_may_spend_resources_to_accelerate_recovery`
*   `attacker_success_may_trigger_temporary_influence_but_not_permanent_theft`
*   `recovery_costs_scale_with_domain_level_and_recent_damage`
*   `domain_residue_persists_after_recovery`

## Domain Protection State Contract (`domain_protection_state.schema.json`)

This JSON Schema validates the state of a domain's active protection and recovery status.

### Key Fields:

*   `protection_state_id`, `domain_state_id`, `owner_player_id`: Identifiers and context.
*   `current_protection_state`: References one of the defined `protection_states`.
*   `triggering_resolution_id`: The ID of the invasion resolution that initiated this state (or null).
*   `recent_attack_count`, `same_attacker_repeat_count`: Metrics for anti-griefing rules.
*   `recovery_required`, `recovery_progress`: Booleans and a float (0.0-1.0) indicating active recovery status.
*   `protection_expires`: True if the current protection has a time limit.
*   `permanent_immunity_granted`: Must be `false`.
*   `domain_recoverable`: Must be `true`.
*   `playability_restored_before_next_invasion`: Must be `true`.
*   `escalating_cost_required_for_repeat_attack`: Must be `true`.
*   `forbidden_flags`: Boolean flags (`permanent_domain_lock`, `permanent_immunity`, `unrecoverable_damage`, `repeat_attack_without_cost`, `full_conquest_from_failed_safe`) that must *always* be `false` to prevent exploits and ensure fair play.

## Example Domain Protection State (`example_domain_protection_state.json`)

This file provides a concrete example of a domain in a `RECOVERY_WINDOW` state after an invasion. It shows tracking of recent and repeat attacks, partial recovery progress, and explicitly sets `permanent_immunity_granted` to `false`, `domain_recoverable` to `true`, and all `forbidden_flags` to `false`, aligning with the anti-griefing and recoverability principles.

## Validation and Integrity

The validation script (`tests/validate_domain_protection_rules.py`) ensures:
*   The `domain_protection_registry.json` exists, declares at least 5 protection states, and includes required anti-griefing and recovery rules.
*   The `domain_protection_state.schema.json` is a valid JSON Schema.
*   The `example_domain_protection_state.json` validates successfully against the schema.
*   The example explicitly sets `domain_recoverable` to `true`, `permanent_immunity_granted` to `false`, `protection_expires` to `true`, and `playability_restored_before_next_invasion` to `true`.
*   All `forbidden_flags` in the example are `false`.
