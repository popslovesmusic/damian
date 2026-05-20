# Combat Equipment Pressure Integration

This document explains how bounded equipment pressure influences deterministic combat resolution in the Tower Engine.

## Overview

Equipment in the Tower Engine is not just a source of power; it is an **operational tradeoff**. The `combat_resolution_stub` has been extended to incorporate aggregate pressure from a player's equipment loadout to bias outcomes and generate economic/structural evidence.

## Integration Logic

The stub uses the following rules to translate equipment pressure into combat consequences:

1.  **Repair Pressure -> Resource Pressure**: High repair pressure (> 0.5) on gear automatically flags the session as having high "Resource Pressure Observed." This represents the increased gold and material drain required to maintain the gear after the encounter.
2.  **Residue Visibility -> Residue Pressure**: High visibility gear (> 0.6) increases total residue visibility, making it more likely that the session is flagged as having high "Residue Pressure Observed."
3.  **Mutation Affinity**: Gear sensitivity to mutations is reported in the combat result. While it does not bypass mutation generation rules, it provides the foundation for future items that may stabilize or destabilize floor environments.
4.  **Capacity Pressure -> Retreat Risk**: High capacity pressure (> 0.8), representing a heavy or cumbersome loadout, biases the system towards a `RETREAT_TO_HUB` outcome if resource usage (potions) is also high.
5.  **Risk Profile -> Defeat Risk**: Volatile gear with a high risk profile (> 0.7) increases the effective enemy pressure, potentially pushing a high-stakes encounter into a `DEFEAT_DROP` outcome.

## Boundedness and Safety

This integration remains strictly bounded:
*   **Pipeline Preservation**: All outcomes are still routed through the `mvp_outcome_pipeline`. Equipment cannot bypass the consequences of defeat or the structural changes triggered by mutations.
*   **Consequence Integrity**: Gear can mitigate risk or absorb pressure, but it cannot grant invulnerability or cancel residue generation.
*   **Reporting vs. Runtime**: This is a "stub integration." It uses aggregate numbers to bias deterministic outcomes for auditing and testing, rather than implementing a full real-time equipment system.

## Observed Evidence

The structured combat result now includes:
*   `equipment_pressure_used`: Confirms gear influence was active.
*   `repair_pressure_observed`: True if gear upkeep was a significant factor.
*   `equipment_residue_visibility_observed`: True if gear significantly increased residue exposure.
*   `equipment_mutation_affinity_observed`: True if gear was sensitive to the floor's instability.
