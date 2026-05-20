# Stage 017: Manual Route Selection and Spatial Agency Review

## Overview
This stage focused on transforming traversal from a semi-automatic movement mechanism into explicit strategic spatial agency. Players now knowingly choose risk corridors, scarred regions, unstable routes, and territorial pressure paths based on partial hazard information.

## Accomplishments
1. **MVP Manual Route Selection Boundary**: Defined contracts and boundaries for manual route choices.
2. **Minimal Route Selection Stub**: Added logic allowing players to select explicit paths (e.g. `pressure_route`, `primary_route`).
3. **Console Integration**: Integrated `traverse` as an explicit command (alias of `advance`) that accepts specific `route_id` arguments.
4. **Route Hazard Visibility**: Modeled "Route Recon", where a route's true hazards are obscured by limited information accuracy.
5. **Dashboard & Transcripts**: Surfaced the "Route Recon" visibility data in the console's `status` output and included it within replay transcripts.

## Architectural Assessment
- The data structures (`route_visibility_snapshot.schema.json`, `manual_route_selection.schema.json`) correctly ensure that the player is operating under uncertainty (`route_visibility_must_be_partial_not_perfect_information`).
- All existing tests pass, and integration works natively with the console session loop.

## Looking Ahead
The framework is in place to have routes change state and degrade. As we move to **STAGE-018: Territorial Instability and Foothold Collapse**, we can use this explicit route selection foundation to make routes fundamentally unsafe, forcing players to dynamically adapt.