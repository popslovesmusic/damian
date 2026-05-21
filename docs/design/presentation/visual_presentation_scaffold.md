# Visual Presentation Scaffold

## Overview
Stage 068 introduces a visual presentation layer to the Playable Vertical Slice, transforming the architectural scaffolding into a recognizable, albeit placeholder-driven, prototype. The objective is to provide a clear visual identity for the game's core elements – character, enemies, environment, and HUD – without implying final art direction. This ensures the playtesters and developers can interact with a visually readable version of the Tower while maintaining focus on core gameplay mechanics.

## Visual Presentation Contract
The `engine/presentation/visual_presentation_contract.json` lays out the strict rules governing this visual layer:
-   **Placeholder-Safe Visuals**: All visual assets (represented by ASCII symbols in this CLI context) must clearly communicate their function without any pretense of being final production art.
-   **Survival-Critical HUD**: The Head-Up Display must expose essential survival information (health, stamina, pressure, resources, location) clearly and non-obtrusively.
-   **Runtime-State Reflective Feedback**: Visual feedback (e.g., damage indicators, pressure warnings) must directly reflect the actual runtime state as processed by the underlying managers.
-   **Continuation Data Alignment**: The death and recovery screens must accurately present information derived from the `ContinuationManager`.
-   **Manifest-Tracked Assets**: All placeholder assets are documented in `engine/presentation/placeholder_asset_manifest.json` for auditable clarity.

## Visual Scaffold Manager
The `engine/presentation/visual_scaffold_manager.py` is the core component for generating this visual output. It:
-   **Interprets Game State**: Consumes the current `game_state` and `audits` from the `PlayableSliceManager`.
-   **Generates HUD**: Creates dynamic HUD elements (health/stamina bars, pressure indicator, resource counts) based on `hud_profile.json`.
-   **Renders Scene**: Generates a simplified ASCII map layout showing the player, enemies, and resources.
-   **Presents Feedback**: Displays visual feedback for events like combat and death/recovery, ensuring alignment with `ContinuationManager` data.
-   **Visualizes Audit**: Provides a simplified visual audit overlay for immediate feedback on recent events.

## Integration with Playable Slice
The `PlayableSliceManager` (`engine/runtime/playable_slice_manager.py`) has been updated to integrate the `VisualScaffoldManager`. After every action and state change, the `PlayableSliceManager` now calls upon the `VisualScaffoldManager` to render the current visual state, which is then captured in the session's `visual_log`.

## Audit and Verification
The `tests/validate_visual_presentation_scaffold.py` script ensures that:
-   Visual output is consistently generated throughout the simulated gameplay.
-   The generated visuals adhere to the placeholder-safe rule, using ASCII symbols effectively.
-   The HUD correctly displays survival-critical information.
-   The death and recovery screens accurately reflect continuation data.
-   New admin terminal commands (`visual status`, `visual audit`) allow for external inspection of the presentation layer.

## Conclusion
Stage 068 successfully provides a visually readable identity to the playable vertical slice. By adhering to placeholder-safe graphics and ensuring direct reflection of runtime state, the Tower prototype now offers a more immersive and understandable experience for testing, without implying final art direction. This allows for focused iteration on gameplay mechanics while providing essential visual feedback, fulfilling the core objective of making the playable slice visually readable without pretending to be final production art.
