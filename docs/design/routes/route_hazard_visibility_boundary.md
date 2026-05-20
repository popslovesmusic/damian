# Route Hazard Visibility Boundary

## Overview
This boundary governs the information a player receives before they select a route. In order to preserve the Tower's mystery and danger, the information provided must always be partial.

## Strict Rules
- route_visibility_must_be_partial_not_perfect_information
- route_selection_must_preserve_operational_uncertainty
- no_rendered_map_runtime
- no_full_minimap_system

## Contracts
- `route_visibility_snapshot.schema.json` dictates the format of hints and hazards visible to the player from a distance.