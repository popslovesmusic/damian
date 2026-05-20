# Console Manual Route Selection

## Overview
Patch TOWER-ENGINE-135 introduces manual route selection to the MVP console.

## Implementation
- Added `traverse` as an alias for the `advance` command.
- Players can type `traverse [route_id]` to manually select a specific route to take.
- If no route ID is provided, the system falls back to automatic strategic bias selection (preferring primary routes).
- Added visibility into available routes via the `routes` command.

## Rules
- Must preserve operational uncertainty by relying on the underlying hazard stubs.
- Selection generates an artifact capturing the strategic bias of the player's choice.
