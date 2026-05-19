# Minimal Enemy Pressure Selector

## Overview
The Minimal Enemy Pressure Selector is a deterministic runtime component responsible for selecting appropriate enemy archetypes based on floor state, residue history, and mutation levels. It serves as the primary bridge between the tower's adaptation state and the combat pressure experienced by the player.

## Deterministic Selection
To ensure a consistent experience (until the floor state explicitly changes), the selector uses a hashing mechanism derived from `floor_id`, `mutation_level`, `stability`, and `residue_history`. This ensures that for the same set of inputs, the same enemy archetype is always selected.

## Residue Adaptation Biases
The selector applies weights to different archetypes based on player performance and tower state:
- **Direct Pressure**: Favored on floors with low mutation levels and minimal residue history.
- **Attrition**: Biased when residue history indicates high resource usage (e.g., frequent potion consumption).
- **Counter-Measures**: Manifests when the tower detects repeated player strategies through residue analysis.
- **Ambushes**: Triggered by high floor instability, punished sloppy routing or repetitive movement patterns.

## Bounded Pressure Profiles
The selector produces **Enemy Pressure Profiles** that strictly adhere to the engine's boundary rules:
- **Base Pressure Rating**: A normalized value (0.0 to 1.0) derived from mutation level and floor state.
- **Bounded Rules**: Explicit flags (e.g., `unavoidable_defeat`) that must remain `false` to prevent scope creep into non-deterministic or unfair territory.
- **Adaptation Reasoning**: Human-readable descriptions explaining *why* the tower chose a specific pressure source.

## Non-Playable Boundary
This component does not implement:
- **Spawning**: No actual enemies are placed on a map.
- **AI**: No behavior trees or real-time logic.
- **Rendering**: No visual assets are involved.

The output is purely logical data that feeds into the combat resolution stub to influence outcome probabilities.
