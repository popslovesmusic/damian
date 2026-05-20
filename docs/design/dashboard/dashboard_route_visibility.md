# Dashboard Route Visibility

## Overview
Patch TOWER-ENGINE-138 integrates route hazard visibility into the Domain Dashboard Snapshot.

## Implementation
- `derive_route_visibility_summary` aggregates reconnaissance evidence across baseline routes.
- Summarizes average information accuracy and the best visibility band.
- Extracted into the snapshot payload for long-term analytical tracking.

## Rules
- Route visibility must be partial, not perfect information (maximum accuracy is capped below 1.0, e.g., 0.8 with claims).
- Adds value to localized strategic footholds (domain claims) by increasing recon accuracy.
