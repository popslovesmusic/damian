# Audio Atmosphere and Pressure Feedback

## Overview
Stage 069 establishes the Tower's emotional identity through procedural sound, environmental audio, and survival-state feedback. This stage integrates an audio layer into the playable vertical slice, ensuring that the soundscape dynamically reflects the survivor's state and the Tower's inherent hostility, without overwhelming crucial survival clarity.

## Audio State Contract
The `engine/audio/audio_state_contract.json` defines the core rules for the audio system:
-   **Pressure-Reactive Audio**: Sound must dynamically reflect the runtime pressure state, with subtle cues for low, medium, and high pressure.
-   **Intentional Silence**: Periods of silence are deliberately used to heighten tension and prevent auditory fatigue.
-   **Readable Enemy Cues**: Enemy audio (e.g., proximity growls, attack telegraphs) must be clear and distinct.
-   **Procedural Music Layering**: Music adapts dynamically to gameplay events and pressure levels, using placeholder tracks.
-   **Clarity Over Overload**: Audio should enhance survival clarity, not obscure it.
-   **Replaceable Placeholders**: All audio assets are placeholders, tracked for easy replacement with production-quality assets.

## Procedural Audio Profile and Music Layer Manifest
*   **`engine/audio/procedural_audio_profile.json`**: Specifies rules for procedural audio events, such as when a heartbeat sound triggers at low health, or a pressure escalation effect plays.
*   **`engine/audio/music_layer_manifest.json`**: Defines placeholder music tracks and their conditions for active layering, allowing dynamic transitions between ambient, tension, combat, and death/recovery states.

## Audio Pressure Manager
The `engine/audio/audio_pressure_manager.py` is the central component for generating the audio experience. It:
-   **Interprets Game State**: Consumes current `game_state`, `event` data (e.g., "COMBAT", "DEATH_EVENT"), and audio feedback profiles from other managers.
-   **Generates Audio Cues**: Produces text-based descriptions of active sound effects, such as ambient hums, pressure feedback, health feedback (heartbeat), combat impacts, and traversal sounds.
-   **Manages Music Layers**: Determines which music layers are active based on game state (e.g., pressure levels, combat status) and events.

## Integration with Playable Slice
The `PlayableSliceManager` (`engine/runtime/playable_slice_manager.py`) has been updated to:
-   Import and initialize the `AudioPressureManager`.
-   Pass relevant game state and event information (including combat and traversal audio feedback) to the `AudioPressureManager` at each step.
-   Capture the generated text-based audio output in `self.audio_log` within the session report.
The `VisualScaffoldManager` (`engine/presentation/visual_scaffold_manager.py`) has also been updated to display the current audio state as part of the HUD, making the simulated audio perceivable within the CLI environment.

## Admin Terminal Integration
The `RestrictedAdminTerminal` (`engine/os_boundary/restricted_terminal.py`) has been extended with:
-   **`audio status` command**: Reports a summary of the current audio atmosphere and pressure feedback, including verdict and status of audio generation, pressure reflection, and enemy cues.
-   **`audio audit` command**: Provides a full audit of the generated audio output and music layers from the `stage_069_audio_pressure_audit.json` file.

## Audit and Verification
The `tests/validate_audio_pressure_runtime.py` script ensures that:
-   Audio output is consistently generated throughout the simulated gameplay.
-   The audio output correctly reflects runtime pressure and health states.
-   Enemy audio cues (simulated by combat impact sounds) are present.
-   Music layers are procedurally reacting to game state.
-   The Admin terminal can safely report the status and audit of the audio system.

## Conclusion
Stage 069 successfully establishes the emotional identity of the Tower through procedural sound and pressure-responsive atmosphere. By integrating dynamic audio feedback into the playable vertical slice, the prototype gains a crucial layer of immersion and survival clarity, further solidifying the core identity of the Tower as a hostile and emotionally resonant environment.
