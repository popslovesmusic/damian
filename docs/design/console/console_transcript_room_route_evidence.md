# Console Transcript Room Route Evidence

This document explains how the console transcript reporting system captures and records topological room route evidence.

## Overview

The `console_transcript_reporter` has been extended to capture evidence of the player's topological spatial navigation. This ensures that when a player chooses a specific path through a floor's room graph, the resulting environmental hazards, exposure levels, and escape modifiers are materially recorded and reviewable.

## Captured Evidence

The transcript now includes the following room route observability fields:

*   **`room_graph_evidence_observed`**: A boolean flag indicating if floor topography was materially assessed.
*   **`room_route_evidence_observed`**: A boolean flag indicating if specific room-to-room routes were generated and used.
*   **`room_routes_observed`**: An integer count of all logical topological routes generated during the session.
*   **`selected_routes_observed`**: An array of unique route IDs chosen by the player (or system) for navigation.
*   **`route_types_observed`**: An array of the strategic types of routes encountered (e.g., `primary_route`, `escape_route`).
*   **`environmental_profiles_observed`**: An array of the granular hazard profiles (darkness, instability, etc.) of the chosen paths.
*   **`route_exposure_values_observed`**: An array of aggregate hazard levels encountered during spatial navigation.
*   **`highest_route_exposure_observed`**: Tracks the maximum environmental hazard encountered across all chosen routes.
*   **`escape_modifiers_observed`**: An array of values associated with how much a route influenced escape safety.
*   **`route_pressure_used_observed`**: A boolean confirming that route-specific hazards were integrated into the total traversal pressure.
*   **`room_route_summaries`**: An array of human-readable strings preserving the strategic context and hazard level of every spatial choice.

## Integration Flow

1.  **Traversal Command**: A spatial command (e.g., `advance` or `escape`) is executed.
2.  **Topological Assessment**: The console builds the current floor's `RoomGraph` and generates routes via `room_traversal_route_builder`.
3.  **Payload Extraction**: The transcript reporter inspects the command result `payload` for the `room_graph`, `room_routes`, and `selected_route`.
4.  **Aggregation**:
    *   Route counts are incremented.
    *   Selected route hazards and modifiers are added to their respective arrays.
    *   Maximum values are updated to track peak environmental hazard.
5.  **Audit Recording**: The aggregated evidence is written to the transcript JSON in `outputs/console_transcripts/`.

## Strategic Observability

By capturing topological hazards, auditors can review the "journey" as a series of specific spatial tradeoffs. Transcripts reveal if a player is successfully navigating the Tower's most dangerous corridors or if they are using safer "Recovery Routes" to manage their material burden. This reinforces the core principle that every spatial choice in the Tower—not just every combat—carries a physical and auditable consequence.
