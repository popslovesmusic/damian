# Minimal Room Traversal Route Builder

This document explains the deterministic room traversal route builder implementation for the Tower Engine MVP.

## Overview

The `room_traversal_route_builder` is responsible for generating logical and material routes between rooms in a floor graph. It turns simple graph edges into **material strategic paths** by calculating specific environmental hazards and escape risks for every connection.

## Route Types and Rules

To ensure a balanced spatial economy, routes are classified into several types, each with unique strategic properties:

1.  **Primary Route**: The main path to the exit. Always critical and preserves playability.
2.  **Side Route**: Optional exploration paths. Usually carry higher exposure but are not required for floor completion.
3.  **Recovery Route**: Paths leading to recovery rooms. They have reduced enemy exposure and provide an `escape_modifier` bonus.
4.  **Pressure Route**: Hazardous paths required for progress. They have increased resource drain and a negative `escape_modifier`.
5.  **Survivor Mark Route**: Paths leading to unclaimed survivor marks. They are unstable and carry higher mutation scarring.
6.  **Escape Route**: Paths optimized for retreating. They have very low enemy exposure and the highest `escape_modifier`.

## Environmental Profiles

Every route is defined by an **Environmental Profile**, which aggregates five key material hazards:

*   **Darkness**: Affects visibility and stealth.
*   **Instability**: Influences the likelihood of the route changing or becoming blocked.
*   **Enemy Exposure**: Determines the probability of combat encounters on the path.
*   **Resource Drain**: Represents the attrition of supplies (stamina, items) during the journey.
*   **Mutation Scarring**: The degree to which the path is permanently altered by previous residues.

## Determinism and Clamping

*   **Node-Driven**: All hazards are derived from the `difficulty_rating` and `stability` of the connected nodes, ensuring that a route's hazard level is consistent with the rooms it connects.
*   **Weighted Exposure**: `route_exposure` is a weighted average of the profile hazards, providing a single auditable hazard value (0.0 to 1.0).
*   **Bounded Results**: All profile values and aggregate hazard scores are strictly clamped to their valid ranges, preventing inflationary strategic risk.

## Integration Flow

1.  **Graph Generation**: The `room_graph_builder` creates the floor's topological structure.
2.  **Route Building**: The builder iterates over every node connection and generates a `RoomTraversalRoute`.
3.  **Strategic Choices**: The player chooses between available routes based on their current material burden and the reported hazard levels.
4.  **Audit Trail**: Every generated route is recorded and validated, ensuring a consistent spatial history in transcripts.

## Non-Map Boundary

This builder is strictly responsible for **generating route data**. It does not handle:
*   Visual rendering of corridors.
*   Real-time pathfinding algorithms.
*   Character animation during movement.
