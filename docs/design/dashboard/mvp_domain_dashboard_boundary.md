# MVP Domain Dashboard Boundary

This document defines the foundational framework for the Domain Dashboard in the Tower Engine.

## Philosophy: Survival Cognition, not Cosmetic UI

In the Tower Engine, the dashboard is not a decorative overlay or a "social" interface. Instead, it is **Survival Cognition Infrastructure**. Its primary purpose is to make the compounding hazards and recursive history of the Tower cognitively readable, enabling the player to make informed meta-strategic decisions.

## Pressure Visibility

The dashboard aggregates material evidence from all core subsystems to surface current survival pressure:

1.  **Survival Pressure**: A weighted summary of current tactical hazard (combat, traversal, escape risk).
2.  **Operational Burden**: The physical "drag" of inventory weight and gear condition.
3.  **Mutation Exposure**: The degree to which the Domain has been destabilized by previous deaths and residue.
4.  **Residue History**: A chronological record of the "scars" left on the Tower's memory.

## Runtime Responsibilities

The Domain Dashboard runtime is responsible for:

*   **Surfacing Pressure**: Making complex material hazards legible at a glance.
*   **Tracking History**: Maintaining a recursive record of runs, routes, and residues.
*   **Preserving Readability**: Ensuring that strategic information is clear and actionable without overwhelming the player.
*   **Supporting Auditability**: Providing structured snapshots that can be recorded in transcripts for post-run analysis.

## Identity Rules

*   **No Perfect Information**: The dashboard surfaces known hazards and history; it does not reveal "hidden" future events or map layouts yet to be explored.
*   **Preserve Uncertainty**: Legibility does not equal safety. Knowing the exact escape risk does not make the escape itself any easier.
*   **Bypass Prohibited**: The dashboard exists to *inform* gameplay, not to replace it. It cannot be used to automate combat, bypass floor progression, or erase residue.

## Future Path

In future patches, this boundary will be implemented as a functional Snapshot Builder. The console will be updated to produce periodic dashboard snapshots, turning the engine's net economy into a readable strategic status report.
