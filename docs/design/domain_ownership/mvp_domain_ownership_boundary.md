# MVP Domain Ownership Boundary

This document defines the foundational framework for Domain Ownership in the Tower Engine.

## Philosophy: Meta-Strategic Maintenance, not Absolute Safety

In the Tower Engine, owning a floor is not about creating a "safe house" that ignores the game's core rules. Instead, it is **Meta-Strategic Maintenance**. By spending "Stability Shards" (looted from the Tower), players can claim dominion over specific floors, allowing them to actively manage the environment's instability.

## Stability and Shards

The core mechanic of ownership is the investment of material resources:

1.  **Stability Shards**: These represent fragments of the Tower's original order. They are the primary currency for establishing and maintaining dominion.
2.  **Stability Level**: A measured value (0.0 to 1.0) representing how "ordered" an owned floor is. Higher stability materially reduces the chance of hazardous replay mutations.
3.  **Upkeep Cost**: Dominion is not permanent. It requires a constant influx of shards (per run) to counteract the natural entropy of the Tower.

## Runtime Responsibilities

The Domain Ownership runtime is responsible for:

*   **Tracking Dominion**: Recording which floors are owned and by whom.
*   **Mitigating Mutations**: Using stability levels to bias mutation generation toward less hazardous outcomes.
*   **Consuming Shards**: Materially deducting shards from the player's meta-inventory for establishing or maintaining control.
*   **Reporting Status**: Making ownership and stability levels clearly visible in the Domain Dashboard.

## Identity Rules

To maintain engine integrity, ownership follows these strict rules:

*   **No Defeat Bypass**: Owning a floor does not prevent combat defeat or the material consequences of a `DEFEAT_DROP`.
*   **No Residue Erasure**: Establishing dominion does not erase previous residues; it only manages the *future* impact of that residue (mutations).
*   **Material Investment**: Control always requires the expenditure of material wealth. There is no "free" territory in the Tower.
*   **Bounded Visibility**: Ownership status and stability metrics remain auditable in session transcripts.

## Future Path

In future patches, this boundary will be implemented as a functional Ownership Stub. The console will be updated to allow players to execute `claim` and `stabilize` commands, turning looted "Stability Shards" into a meta-strategic tool for territory management.
