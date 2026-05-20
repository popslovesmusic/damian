# MVP Durability Decay Boundary

This document defines the foundational framework for bounded equipment durability decay in the Tower Engine.

## Philosophy: Operational Wear vs. Item Deletion

In the Tower Engine, durability decay is not designed as a "punishment" or a mechanism for random item deletion. Instead, it is an **operational burden** that reinforces the strategic necessity of resource management:

1.  **Materialized Strain**: Equipment condition deteriorates through the physical strain of combat, mutation instability, and even the burden of a heavy inventory (high capacity pressure).
2.  **Strategic Maintenance**: Durability loss creates a material demand for repair materials, closing the "maintenance loop" established in Stage 008.
3.  **No Permanent Breakage (MVP)**: For the MVP phase, gear may reach zero durability and lose its operational effectiveness, but it will not be permanently deleted. This ensures that the core identity of specific items is preserved while still enforcing the consequence of neglect.

## Decay responsibilities

*   **Tracking**: Accurately maintain current and maximum durability values.
*   **Applying Decay**: Calculate and deduct durability loss based on encounter intensity and equipment risk profiles.
*   **Reporting**: Every decay event must report the "Decay Pressure" context (combat, capacity, mutation) to provide an audit trail for the item's deterioration.
*   **Guarding Bounds**: Ensure that durability never drops below zero and that all anti-inflationary flags are preserved.

## Identity Rules (Consequence Preservation)

To maintain engine integrity, the durability system follows these strict rules:

*   **No Defeat Cancellation**: Having high durability gear cannot prevent the consequences of `DEFEAT_DROP`.
*   **No Residue Bypass**: Maintaining gear condition does not prevent the generation of residue from player actions.
*   **No Invulnerability**: Durability can absorb pressure but never grant permanent invulnerability to the player or the gear itself.
*   **Operational Tension**: Decay must scale with the actual pressure of the floor, ensuring that deeper exploration carries a compounding material cost.

## Future Path

In future patches, this boundary will be implemented as a functional runtime. The `repair` command will be updated to consume the materials tracked in Stage 008 to restore the durability lost in combat, finalizing the engine's core economic cycle.
