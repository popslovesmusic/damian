# MVP Manual Route Selection Boundary

## Overview
Defines the data boundaries for how a player chooses their path.
The system does not provide a visual map or real-time pathfinding, maintaining uncertainty and a focus on textual or conceptual path choices.

## Strict Rules
- no_rendered_map_runtime
- no_real_time_pathfinding
- no_open_world_navigation
- route_selection_must_preserve_operational_uncertainty
- manual_route_selection_must_increase_spatial_agency_without_removing_fear

## Contracts
- `manual_route_selection.schema.json` dictates the selection of routes from a current node.