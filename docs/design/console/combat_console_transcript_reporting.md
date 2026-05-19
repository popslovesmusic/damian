# Combat-Aware Console Transcript Reporting

## Overview
The Console Transcript Reporter has been extended to capture detailed evidence of combat encounters. This allows for the review of deterministic combat resolutions and their subsequent effects on the project's reactive systems (mutation, survivor marks, and residue).

## Extended Transcript Fields
In addition to standard command logs, transcripts now include the following combat-specific fields:

- **`combat_sessions_observed`**: Total number of combat encounters triggered.
- **`combat_outcomes_observed`**: An ordered list of all combat outcomes (`VICTORY_ASCEND`, `DEFEAT_DROP`, `RETREAT_TO_HUB`).
- **`combat_victories_observed`**: Count of successful combat outcomes.
- **`combat_defeats_observed`**: Count of failed combat outcomes.
- **`combat_retreats_observed`**: Count of safe retreats from combat.
- **`resource_pressure_observed`**: Boolean flag indicating if high resource usage (e.g., potion drain) was detected during a session.
- **`residue_pressure_observed`**: Boolean flag indicating if build visibility or strategy repetition reached critical levels.
- **`mutation_after_combat_observed`**: Specifically tracks if a floor mutation occurred as a result of a combat defeat.
- **`survivor_mark_after_combat_observed`**: Specifically tracks if a survivor mark was attached following a combat defeat.

## Integration with Reactive Systems
The transcript reporter hooks directly into the payload of the `combat` command. Because the `combat` command uses the `mvp_outcome_pipeline`, the transcript captures the full chain of evidence:
1.  **Combat Resolution**: Deterministic outcome based on stats and pressure.
2.  **Pipeline Execution**: Progression updates and residue writing.
3.  **Reactive Feedback**: Triggering of mutations and marks on defeat.

## Observability and Evidence
Transcripts provide high-fidelity evidence that combat resolutions are correctly influencing the tower state. This allows developers to verify that "dominant builds" are indeed accumulating pressure and that defeats are producing the expected world changes without needing real-time combat execution.
