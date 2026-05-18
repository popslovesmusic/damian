# Tower Engine Multiplayer Sessions and Domain Invasions

This document defines the architectural patterns and contractual agreements for small-session multiplayer experiences within the Tower Engine, encompassing cooperative play, domain invasion, defense, and conquest outcomes. The system focuses on defining the structure and rules without implementing live networking.

## Core Principles

*   **Small Sessions Only:** Multiplayer sessions are designed for a limited number of participants (2-4 players) to maintain focus and manage complexity.
*   **Declared Session Authority:** The authority model for each session type is explicitly declared, with a preference for server-authoritative for critical state to prevent cheating and ensure fairness.
*   **Domain Invasion Preserves Playability:** Even after an invasion, a domain must always remain playable and traversable. No invasion can lead to an impossible or soft-locked domain.
*   **Risk-Equals-Advantage:** Both attackers and defenders must incur costs or risks for any advantages they employ, reinforcing the strategic depth and preventing runaway power.
*   **Safe Resolution for Disconnects:** Session disconnects must resolve to a safe, unresolved state, minimizing player frustration and data loss.
*   **Residue Integration:** Invasion outcomes (success or failure for either side) must write residue to both attacker and defender, feeding back into the Tower's adaptive systems.

## Multiplayer Mode Registry (`multiplayer_mode_registry.json`)

This registry declares the supported multiplayer modes and defines the fundamental assumptions about session authority.

### Supported Modes:

*   **`solo`**: Single-player tower/domain progression.
*   **`private_coop`**: 2-4 player cooperative sessions, typically initiated via room codes or invites.
*   **`domain_invasion`**: One party attempts to attack and conquer another player's home domain.
*   **`domain_defense`**: The owner defends their home domain, either actively or through asynchronous preparations.

### Authority Model:

*   **`preferred`: `server_authoritative`**: For critical game states, especially those impacting domain integrity and rewards.
*   **`prototype_allowed`: `host_authoritative_with_validation`**: A lighter model acceptable for prototyping, but still requiring validation to mitigate exploits.
*   **`client_trust`: `limited`**: Reflects a design where clients are not fully trusted for state changes.
*   **`reason`**: "Domain conquest requires authoritative state to avoid impossible domains, reward spoofing, and unfair invasion outcomes."

### Global Rules:

*   `sessions_are_small_2_to_4_players`
*   `private_room_codes_allowed`
*   `domain_state_is_shared_during_invasion`
*   `loot_policy_must_be_declared`
*   `party_defeat_may_trigger_floor_or_domain_regression`
*   `disconnects_must_resolve_to_safe_unresolved_state`
*   `invasion_success_writes_residue_to_attacker_and_defender`
*   `invasion_failure_writes_residue_to_attacker_and_defender`
*   `no_invasion_may_create_unplayable_domain`

## Multiplayer Session Contract (`multiplayer_session.schema.json`)

This JSON Schema validates the state of an active multiplayer session, ensuring consistency across various modes.

### Key Fields:

*   `session_id`, `mode_id`, `authority_model`, `content_pack_id`, `host_player_id`: Core identifiers and contextual data.
*   `player_ids`: An array of participant player IDs, strictly limited to 1-4 players.
*   `target_domain_state_id`: Optional, specifies the target domain for invasion/defense.
*   `session_state`: The current status of the session (`CREATED`, `LOBBY`, `ACTIVE`, `RESOLVING`, etc.).
*   `loot_policy`: Specifies how loot is handled (`INSTANCED`, `PARTY_ROLL`, `OWNER_LOCKED`, `NO_LOOT`).
*   `risk_profile`: An object detailing `attacker_risk`, `defender_risk`, and `shared_risk` descriptions.
*   `safe_resolution_required`: A boolean indicating that the session must end in a non-corrupted state.

## Domain Invasion Event Contract (`domain_invasion_event.schema.json`)

This JSON Schema validates records of domain invasion events, detailing the actions, outcomes, and consequences for both attackers and defenders.

### Key Fields:

*   `invasion_event_id`, `session_id`: Unique identifiers.
*   `attacker_player_ids`, `defender_player_id`, `target_domain_state_id`, `target_domain_archetype`: Participant and target details.
*   `invasion_cost_paid`: Resources expended by attackers. Must be non-negative.
*   `attacker_advantage_used`, `attacker_risk_incurred`: Lists of specific advantages and risks for attackers.
*   `defender_advantage_active`, `defender_risk_incurred`: Lists of specific advantages and risks for defenders.
*   `outcome`: The result of the invasion (`ATTACKER_CONQUEST`, `DEFENDER_HOLD`, `ATTACKER_RETREAT`, etc.).
*   `residue_written_to_attacker`, `residue_written_to_defender`: Booleans confirming residue generation.
*   `playability_preserved`: Must always be `true`.
*   `forbidden_flags`: Boolean flags (`impossible_domain`, `free_advantage_detected`, `reward_spoof_risk`) that must *always* be `false` to prevent exploits.

## Example Multiplayer Session (`example_multiplayer_session.json`)

This file provides an example of a `domain_invasion` session with two attacking players targeting `domain_state_001`, using `server_authoritative` model, and an `INSTANCED` loot policy. All risks are explicitly outlined, and `safe_resolution_required` is `true`.

## Example Domain Invasion Event (`example_domain_invasion_event.json`)

This file provides a concrete example of a `DEFENDER_HOLD` outcome for a domain invasion, detailing the costs, advantages, and risks incurred by both sides. Critically, all `forbidden_flags` are `false`, `playability_preserved` is `true`, and residue is written to both attacker and defender.

## Validation and Integrity

The validation script (`tests/validate_multiplayer_session_contract.py`) ensures:
*   The `multiplayer_mode_registry.json` exists, declares required modes, and specifies the authority model.
*   Both `multiplayer_session.schema.json` and `domain_invasion_event.schema.json` are valid JSON Schemas.
*   The example session and invasion event payloads validate successfully against their schemas.
*   The `player_ids` array in the example session is within the 1-4 player limit.
*   `safe_resolution_required` is `true` in the example session.
*   Residue is written to both attacker and defender in the example invasion.
*   Attacker and defender advantages are paired with corresponding risks in the example invasion.
*   All `forbidden_flags` in the example invasion are `false`.
