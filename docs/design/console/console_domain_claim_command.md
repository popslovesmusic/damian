# Console Domain Claim Command

This document explains the integration of the `claim` command into the MVP Text Console for establishing localized strategic footholds.

## Overview

The `claim` command has been expanded to support the establishment of **Domain Claims**—localized footholds that provide strategic benefits while carrying operational burdens. This marks the transition from tactical survival to meta-strategic territory management within the console environment.

## Command Usage

The `claim` command is polymorphic, supporting both domain footholds and legacy survivor mark claims:

1.  **Default Domain Claim**:
    *   `claim`
    *   Creates a `recovery_anchor` at the current floor's anchor node.
2.  **Specific Domain Claim**:
    *   `claim <claim_type>`
    *   Creates a foothold of the specified type (e.g., `claim supply_cache`).
3.  **Survivor Mark Claim**:
    *   `claim <mark_id>`
    *   Attempts to claim a survivor mark by its ID (legacy behavior preserved).

### Supported Claim Types

*   `recovery_anchor`: High survival recovery, low maintenance.
*   `supply_cache`: Localized resource hub.
*   `repair_station`: Gear maintenance focus.
*   `survivor_outpost`: High visibility, high recovery foothold.
*   `observation_post`: Low maintenance hazard tracking.

## Meta-Strategic Evidence

When a domain claim is successfully created, the console payload includes critical pressure evidence:

*   **Maintenance Pressure**: The constant resource drain required to hold the foothold.
*   **Visibility Pressure**: How much the foothold attracts environmental hostility (residue).
*   **Mutation Threat**: The specific risk of the foothold being targeted by environmental instability.
*   **Recovery Value**: The material strategic benefit provided by the foothold.

These metrics are also surfaced in the **Domain Dashboard** during `status` checks, enabling players to assess the "net economy" of their established territory.

## Scope Containment

The `claim` command is strictly limited to establishing **data-driven strategic footholds**. It does not introduce:
*   Base-building runtimes or voxel editing.
*   Rendered housing or interior environments.
*   Real-time territory wars or multiplayer synchronization.
*   Any bypass of the engine's core "reward does not erase consequence" principle.
