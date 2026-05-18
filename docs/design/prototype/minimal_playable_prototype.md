# Tower Engine Minimal Playable Prototype System Boundary

This document formally defines the system boundary for the first Minimal Playable Prototype (MPP) of the Tower Engine. The objective of this patch is to precisely freeze the scope of what will be implemented in the initial runtime development phase, preventing scope creep and ensuring a focused approach to proving the core gameplay loop.

## Core Principles

*   **Focus on Core Loop Validation:** The MPP's primary purpose is to prove that the fundamental game loop — player enters floor, encounters enemies, engages combat, handles loot, experiences outcome, and sees environmental adaptation based on residue — is fun and functional.
*   **Minimal Feature Set:** Only the absolutely essential systems required to validate the core loop are included. All other features, regardless of their eventual importance, are explicitly excluded.
*   **No Runtime Implementation Yet:** This patch defines *what* the prototype will include and exclude, but *does not* involve any actual runtime code implementation. Implementation begins in the subsequent patch (`TOWER-ENGINE-017`).
*   **Scalability for Future:** While minimal, the selected systems and contracts established in prior patches are designed to be extensible, allowing for future expansion without refactoring the core architecture.
*   **Clear Exclusion:** Systems explicitly excluded from the MPP are clearly listed to manage expectations and prevent premature development efforts.

## Minimal Playable Boundary (`engine/prototype/minimal_playable_boundary.json`)

This JSON file declares the precise scope of the first playable prototype.

### Prototype Goal:

*   "Prove that a player can enter a generated floor, fight enemies, collect loot, lose or win, write residue, and see a replayed floor mutate while preserving identity."

### Included Systems:

These are the essential components that will be implemented for the MPP:

*   `single_player_runtime`
*   `basic_player_controller`
*   `basic_enemy_controller`
*   `basic_combat`
*   `simple_loot_drops`
*   `three_floor_progression` (a limited number of floors to test progression)
*   `defeat_drop_one_floor` (a specific mechanic to test residue-driven changes)
*   `floor_memory_write`
*   `basic_residue_capture`
*   `basic_floor_mutation`
*   `hidden_survivor_mark_stub` (placeholder for discoverable secrets)
*   `local_json_save` (basic persistence)

### Excluded Systems:

These systems are explicitly out of scope for the MPP:

*   `live_multiplayer`
*   `domain_invasion_runtime`
*   `domain_dashboard_ui`
*   `full_campaign_story`
*   `advanced_gpu_compute`
*   `real_money_economy`
*   `public matchmaking`
*   `procedural content marketplace`
*   `large-scale MMO systems`

### Prototype Limits:

Specific quantitative limits to ensure the prototype remains small and manageable:

*   `players`: 1
*   `floors`: 3
*   `enemy_types`: 3
*   `bosses`: 1
*   `skills`: 3
*   `loot_items`: 20
*   `mutation_rules`: 5
*   `survivor_marks`: 3
*   `content_pack`: "damian" (specifying the target content for the prototype)

### Success Condition:

*   "Player reaches floor 3, is defeated, drops to floor 2, and floor 2 is recognizably the same but changed by residue." This is the core metric for MPP success.

## Prototype Readiness Check Contract (`prototype_readiness_check.schema.json`)

This JSON Schema validates a record indicating whether the architectural groundwork is complete and the repository is ready for runtime implementation.

### Key Fields:

*   `readiness_check_id`, `prototype_id`, `content_pack_id`: Identifiers for the check and prototype.
*   `required_prior_patches_passed`: An array of patch IDs that must have been successfully completed. This lists all patches from `TOWER-ENGINE-001` to `TOWER-ENGINE-015`.
*   `included_systems_confirmed`, `excluded_systems_confirmed`: Arrays confirming adherence to the specified system lists.
*   `scope_creep_detected`: Must be `false`. A flag to catch any unintended feature creep.
*   `ready_for_runtime_implementation`: Must be `true`, indicating that implementation can now commence.
*   `implementation_start_patch`: The patch ID for the actual runtime implementation start (`TOWER-ENGINE-017`).

## Example Prototype Readiness Check (`example_prototype_readiness_check.json`)

This file provides a concrete example of a valid readiness check, confirming that all prior architectural patches have passed, the included/excluded systems are correct, `scope_creep_detected` is `false`, and `ready_for_runtime_implementation` is `true`, targeting `TOWER-ENGINE-017` as the start of implementation.

## Validation and Integrity

The validation script (`tests/validate_minimal_playable_prototype.py`) ensures:
*   The `minimal_playable_boundary.json` exists and meets the specified limits (e.g., 3 floors, 3 enemy types, 1 boss).
*   The `prototype_readiness_check.schema.json` is a valid JSON Schema.
*   The `example_prototype_readiness_check.json` validates successfully against the schema.
*   The example explicitly confirms specific included and excluded systems.
*   `ready_for_runtime_implementation` is `true` and `scope_creep_detected` is `false` in the example.
*   The example includes `defeat_drop_one_floor`, `basic_residue_capture`, and `basic_floor_mutation` in its confirmed systems.
