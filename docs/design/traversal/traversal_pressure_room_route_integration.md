# Route-Aware Traversal Pressure Integration

This document explains the integration of granular room traversal routes into the aggregate traversal pressure and escape risk calculation.

## Overview

The `traversal_pressure_stub` has been updated to move beyond floor-to-floor averages. It now incorporates specific evidence from **Room Traversal Routes**, turning the choice of path into a material strategic tradeoff. 

By integrating route-specific hazards (exposure, profiles, modifiers), the "Tower" ensures that where a player goes is as consequential as what they carry.

## Integration Factors

The aggregate hazard calculation now incorporates the following route-aware evidence:

1.  **Route Exposure**: The overall hazardousness of a chosen path (0.0 to 1.0) now acts as a primary weight in the total traversal pressure. Hazardous paths materially increase the friction of the journey.
2.  **Environmental Profile**: Specific hazards within a route provide additional bias to the aggregate hazard:
    *   **Darkness**: Increases aggregate pressure, representing the stress of low visibility.
    *   **Instability**: Acts as a multiplier for movement friction and environmental hazard.
3.  **Escape Modifiers**: Individual routes can now make retreats easier or harder. A positive modifier (from a "Recovery Route") materially lowers the peak escape risk, while a negative modifier (from a "Pressure Route") increases it.

## Calculation Refinement

*   **Weighted Aggregation**: Total traversal pressure is now a weighted sum of Combat Exposure (35%), Mutation Pressure (25%), Route Exposure (20%), Capacity Pressure (15%), and Repair Burden (5%).
*   **Risk Scaling**: Escape risk is derived from the aggregate hazard and route exposure, then adjusted by the route's escape modifier. This ensures that retreating through a dedicated "Escape Route" is materially safer than trying to flee through a hazardous corridor.

## Strategic Observability

Every traversal event now captures the identity and hazards of the chosen route. This ensures that the strategic "journey" is fully auditable in session transcripts, allowing designers to see if players are successfully navigating the Tower's spatial hazards or if they are being overwhelmed by the material cost of their choices.

## Non-Map Boundary

Despite the inclusion of route-aware logic, the system remains strictly non-rendered. It calculates hazard based on logical topological connections rather than character movement on a grid or pathfinding across a rendered map.
