# Console Route Visibility Status

## Overview
Patch TOWER-ENGINE-139 integrates route hazard visibility directly into the console status response.

## Implementation
- The `status` command retrieves the Domain Dashboard Snapshot.
- Extracts the `route_visibility_summary`.
- Appends `Route Recon: <Visibility_Band> (<Accuracy>)` to the main status string.
- Allows players to make informed decisions before initiating a `traverse` or `escape` command.

## Rules
- Operates on partial information, reinforcing the gameplay loop of establishing footholds to increase visibility.
