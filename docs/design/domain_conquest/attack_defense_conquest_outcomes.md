# Tower Engine Domain Attack, Defense, and Conquest Outcome Rules

This document defines the rules and contracts governing the outcomes of multiplayer invasion attempts within player-owned domains in the Tower Engine. It formalizes how domains are attacked, defended, contested, and how the results impact the domain's state, owner, and attackers, all while adhering to principles of fairness, playability, and preventing permanent loss.

## Core Principles

*   **No Permanent Domain Theft:** Domains cannot be permanently stolen. Conquest grants temporary influence or control, but the original owner's claim remains.
*   **Owner Domain Must Remain Recoverable:** Regardless of invasion outcome, the owner's domain must always remain in a state from which it can be recovered and fully played.
*   **Residue for All Parties:** Both attacker and defender actions, successes, and failures must generate residue that influences their respective progression and the Tower's adaptation.
*   **Playability Preserved:** All invasion outcomes must guarantee the continued playability of the domain, preventing soft-locks or impossible states.
*   **Risk-Advantage Equilibrium:** The principles of risk-equals-advantage apply to both attackers and defenders, ensuring balanced costs and benefits for strategic choices.
*   **Unresolved Sessions Cannot Award Full Conquest:** Sessions that end due to disconnects or other unresolved states cannot result in a full conquest.

## Domain Conquest Outcome Registry (`domain_conquest_outcome_registry.json`)

This registry declares the canonical modes through which domain invasion attempts can resolve, along with their high-level effects.

### Outcome Modes:

*   **`ATTACKER_CONQUEST`**:
    *   *Description*: Attacker reaches and claims the domain core objective.
    *   *Attacker Effects*: `conquest_reward_eligible`, `attacker_residue_written`, `temporary_influence_claim_possible`.
    *   *Defender Effects*: `defender_residue_written`, `domain_stability_loss`, `recovery_window_triggered`.
*   **`DEFENDER_HOLD`**:
    *   *Description*: Defender domain repels attacker or attacker party fails.
    *   *Attacker Effects*: `invasion_cost_lost`, `attack_failure_residue_written`, `possible_floor_or_domain_regression`.
    *   *Defender Effects*: `defense_reward_eligible`, `defender_residue_written`, `domain_confidence_gain`.
*   **`ATTACKER_RETREAT`**:
    *   *Description*: Attacker exits before conquest or defeat.
    *   *Attacker Effects*: `partial_residue_written`, `partial_cost_loss`, `no_conquest_reward`.
    *   *Defender Effects*: `minor_residue_written`, `minor_stability_shift`.
*   **`CONTESTED_STALEMATE`**:
    *   *Description*: Session ends after objective progress without clear conquest or hold.
    *   *Attacker Effects*: `partial_residue_written`, `partial_reward_possible`.
    *   *Defender Effects*: `partial_residue_written`, `temporary_instability`.
*   **`SESSION_UNRESOLVED`**:
    *   *Description*: Disconnect or failure prevents a clean result.
    *   *Attacker Effects*: `safe_resolution_required`, `no_full_conquest`.
    *   *Defender Effects*: `safe_resolution_required`, `no_permanent_domain_loss`.
*   **`FAILED_SAFE`**:
    *   *Description*: Validation failure or impossible state forces protected rollback/resolution.
    *   *Attacker Effects*: `invalid_reward_blocked`, `residue_written_as_failed_safe`.
    *   *Defender Effects*: `domain_protected_from_invalid_state`, `residue_written_as_failed_safe`.

### Global Rules:

*   `conquest_grants_influence_not_permanent_theft`
*   `owner_domain_must_remain_recoverable`
*   `attacker_and_defender_residue_must_be_written`
*   `unresolved_sessions_cannot_award_full_conquest`
*   `failed_safe_blocks_rewards_if_validation_fails`
*   `outcomes_must_preserve_domain_playability`
*   `risk_advantage_equilibrium_applies_to_all_parties`

## Domain Conquest Resolution Contract (`domain_conquest_resolution.schema.json`)

This JSON Schema validates the comprehensive record of a resolved domain invasion event, detailing specific impacts on the domain, players, and residue.

### Key Fields:

*   `resolution_id`, `invasion_event_id`, `session_id`, `target_domain_state_id`: Unique identifiers and context.
*   `attacker_player_ids`, `defender_player_id`: Involved players.
*   `outcome_id`: References one of the defined `outcome_modes`.
*   `objective_progress_percent`: Quantitative measure of attacker progress.
*   `attacker_costs_lost`, `defender_costs_incurred`: Financial/resource impact on both sides (non-negative).
*   `attacker_rewards_granted`, `defender_rewards_granted`: Lists of specific rewards.
*   `domain_effects`: An object detailing changes to the domain (`stability_delta`, `deviation_delta`, `temporary_influence_claimed`, `recovery_window_triggered`, `domain_remains_owner_recoverable` which must be `true`).
*   `residue_results`: An object with boolean flags (`attacker_residue_written`, `defender_residue_written`, `domain_residue_written`), all of which must be `true`.
*   `playability_results`: An object with boolean flags (`playability_preserved`, `primary_route_preserved`, `no_softlock_detected`), all of which must be `true`.
*   `forbidden_flags`: Boolean flags (`permanent_domain_theft`, `full_conquest_from_unresolved_session`, `reward_without_resolution`, `impossible_domain_after_resolution`) that must *always* be `false` to prevent exploits.

## Example Domain Conquest Resolution (`example_domain_conquest_resolution.json`)

This file provides a concrete example of a `DEFENDER_HOLD` outcome. It details a specific `objective_progress_percent`, costs incurred, rewards granted, and domain effects. Crucially, `domain_remains_owner_recoverable`, all `residue_results`, and all `playability_results` are `true`, while all `forbidden_flags` are `false`, aligning with the core principles.

## Validation and Integrity

The validation script (`tests/validate_domain_conquest_outcomes.py`) ensures:
*   The `domain_conquest_outcome_registry.json` exists, declares at least 6 outcome modes, and includes specific required modes.
*   The `domain_conquest_resolution.schema.json` is a valid JSON Schema.
*   The `example_domain_conquest_resolution.json` validates successfully against the schema.
*   The example explicitly sets `attacker_residue_written`, `defender_residue_written`, `domain_residue_written` to `true`.
*   The example explicitly sets `playability_preserved`, `primary_route_preserved`, `no_softlock_detected`, and `domain_remains_owner_recoverable` to `true`.
*   All `forbidden_flags` in the example are `false`.
