# Death, Recovery, and Survivor Continuation Runtime

## Overview
Stage 060 defines the infrastructure for survivor death and continuation in the Tower ecosystem. In Damian, death is not a hard reset; it is a systemic transformation where a survivor's defeat leaves behind residue, scars, and world memory, while preserving their long-term identity and continuity through bounded inheritance and recovery mechanisms.

## Continuation Boundary
The `engine/player/contracts/death_continuation_boundary.json` defines the strict safety rules:
- **No Permanent Death**: Account-level permanent death is prohibited. A survivor's identity always survives.
- **Residue Mandatory**: Every death must be recorded as residue in the world, ensuring failure remains meaningful.
- **Recoverability Focus**: All death outcomes must include defined recovery paths (e.g., recovery runs, rescue contracts).
- **No Total Wipe**: Total save wipes are forbidden. Persistence is transformed, not erased.

## Survivor Continuation Contract
The continuation contract (`engine/player/contracts/survivor_continuation_contract.json`) specifies the state after defeat:
1. **Defeat Context**: Records the cause and location of death for world memory.
2. **Residue Carryover**: Defines which systemic pressures or scars are preserved for the next life.
3. **Inheritance Profile**: Specifies which bounded items or sigils are passed to the next iteration of the survivor.
4. **Recovery Options**: Lists available paths for restoring full survivor capacity (e.g., stamina-cost runs).

## Continuation Manager
The `engine/player/runtime/continuation_manager.py` component manages the death lifecycle:
1. **Manifest Generation**: Produces hash-verified continuation manifests that summarize the state of defeat.
2. **Legacy Recovery**: Orchestrates the resolution of recovery runs or rescue contracts to restore survivor identity.
3. **World Memory Updates**: Injects the residue of death into the Tower's procedural history, creating "Fallen Markers" or scarring domains.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `continuation status` and `continuation audit` commands to review survivor death history and verify inheritance bounding.
- **Dashboard**: The player dashboard displays evidence of their "Legacy Lineage" and the current status of any active recovery paths.

## Conclusion
The Survivor Continuation system ensures that Damian remains a journey of persistence. It fulfills the core rule that while the survivor may fall, the Tower remembers, and the journey continues through a cycle of pressure, death, and recovery.
