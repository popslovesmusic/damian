import os
import json
import hashlib
import time

class VoiceSessionManager:
    def __init__(self, contract_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)
        self.active_sessions = {}

    def create_session(self, host_id, mode, participants=None):
        """Creates a bounded voice session."""
        if mode not in self.contract["allowed_modes"]:
            return {"status": "FAIL", "reason": f"Forbidden session mode: {mode}"}

        session_id = f"voice_{host_id}_{int(time.time())}"
        session = {
            "session_id": session_id,
            "host_player_id": host_id,
            "participant_ids": participants or [host_id],
            "session_mode": mode,
            "push_to_talk_enabled": True,
            "voice_presence_state": "ONLINE",
            "created_timestamp": time.time(),
            "bounded_flags": {
                "no_game_authority": True,
                "isolated_routing": True
            },
            "session_hash": ""
        }

        # Calculate session hash
        session_str = json.dumps(session, sort_keys=True)
        session["session_hash"] = hashlib.sha256(session_str.encode()).hexdigest()

        self.active_sessions[session_id] = session
        return session

    def disconnect_session(self, session_id):
        """Closes a session safely without affecting game state."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return {"status": "SUCCESS", "message": "Voice session terminated. Game state preserved."}
        return {"status": "FAIL", "reason": "Session not found."}

class AudioRouter:
    def __init__(self, moderation_path):
        with open(moderation_path, 'r') as f:
            self.moderation = json.load(f)

    def route_audio(self, session, sender_id, receiver_id):
        """Simulates safe audio routing between participants."""
        # Check if sender is in session
        if sender_id not in session["participant_ids"] or receiver_id not in session["participant_ids"]:
             return {"status": "BLOCKED", "reason": "Participant not in session."}
        
        # Simulate PTT check
        if not session["push_to_talk_enabled"]:
             return {"status": "BLOCKED", "reason": "PTT required."}

        return {
            "status": "ROUTED",
            "sender": sender_id,
            "receiver": receiver_id,
            "isolated": True,
            "latency_ms": 20
        }

if __name__ == "__main__":
    # Internal test
    vsm = VoiceSessionManager("engine/network/contracts/audio_session_contract.json")
    router = AudioRouter("engine/network/contracts/audio_moderation_boundary.json")

    session = vsm.create_session("player_gamma", "private_party", ["player_gamma", "player_delta"])
    print(f"Session Created: {session['session_id']}")

    route = router.route_audio(session, "player_gamma", "player_delta")
    print(f"Routing Result: {json.dumps(route, indent=2)}")

    disconnect = vsm.disconnect_session(session["session_id"])
    print(disconnect["message"])
