# Live Audio Chat Boundary

## Overview
Stage 040 defines the boundary for real-time voice communication within the Tower ecosystem. This social layer allows survivors to communicate live while maintaining a strict separation between voice presence and gameplay authority.

## Audio Sessions
Live communication is managed through bounded sessions:
- **Contractual Safety**: All sessions are governed by `engine/network/contracts/audio_session_contract.json`.
- **Modes**: Supported modes include `private_party`, `treaty_channel`, and `domain_echo_observer`. Unrestricted global voice is prohibited.
- **PTT Enforcement**: Push-to-Talk is enabled by default to prevent background recording and ensure intentional communication.
- **Verification**: Sessions are hash-verified and recorded in audit logs to ensure they remain within the defined boundary.

## Separation of Authority
A core rule of the Tower is that voices cannot mutate state.
- **Isolation**: Audio routing (`engine/network/runtime/voice_session_stub.py`) is logically isolated from the game engine's state machine.
- **Presence Only**: Voice presence is tracked as a social state (`ONLINE`, `PUSH_TO_TALK`) but grants no authority over game state or OS administration.
- **Fail-Safe Disconnect**: Losing an audio connection or intentionally disconnecting never affects the player's position, inventory, or domain status.

## Moderation and Safety
The `audio_moderation_boundary.json` defines required features for player safety:
1. **Local Controls**: Mute, disconnect, and local audio disable are always available.
2. **Privacy**: Presence visibility can be toggled, and silent background recording is strictly forbidden.
3. **Auditability**: Flagged interactions and session lifecycle events are recorded in the `TOWER_DATA` partition for diagnostic review.

## Terminal Integration
Admins can monitor the status of live audio sessions through the `audio status` command in the Restricted Admin Terminal. This provides visibility into active sessions and confirms that all social interactions are correctly bounded.

## Conclusion
The live audio chat boundary provides a human connection in the hostile Tower without compromising its asynchronous, authority-controlled nature. It ensures that survivors can coordinate and socialize within a secure and auditable framework.
