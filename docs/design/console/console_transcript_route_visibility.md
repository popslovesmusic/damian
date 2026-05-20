# Console Transcript Route Visibility

## Overview
Patch TOWER-ENGINE-140 captures route visibility and manual route selection data within the console transcripts.

## Implementation
- Collects `route_selections_observed`, tracking manual biases.
- Captures visibility bands and information accuracy arrays.
- Validates the generation of `route_hazard_visibility_summaries` during parsing.

## Rules
- Output serves as the validation artifact for verifying that players interact with the route hazard system and that domain claims are providing their intended reconnaissance benefits.
