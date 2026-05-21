import os
import json
import time
import random

# Import managers from their respective modules
from engine.player.runtime.onboarding_manager import OnboardingManager
from engine.traversal.runtime.movement_feel_manager import MovementFeelManager
from engine.combat.runtime.combat_feel_manager import CombatFeelManager
from engine.enemies.runtime.enemy_ecology_manager import EnemyEcologyManager
from engine.economy.runtime.survival_economy_manager import SurvivalEconomyManager
from engine.player.runtime.continuation_manager import ContinuationManager
from engine.presentation.visual_scaffold_manager import VisualScaffoldManager

# STAGE-069 runtime layering planner
from engine.audio.audio_pressure_manager import AudioPressureManager


class PlayableSliceManager:
    def __init__(self, contract_path):
        with open(contract_path, "r", encoding="utf-8-sig") as f:
            self.contract = json.load(f)

        self.audits = []
        self.state = {
            "survivor_id": "TEST_SURVIVOR",
            "health": 100,
            "stamina": 100,
            "resources": {"FOOD": 50, "WATER": 50, "SCRAP": 20},
            "location": "Starting Zone",
            "biome": "tower",
            "pressure": 0,
            "has_died": False,
            "play_session_id": f"PS_{int(time.time())}",
        }

        # Initialize sub-managers (simplified pathing for prototype)
        base_path = "engine/"
        self.om = OnboardingManager(
            os.path.join(base_path, "player/contracts/first_hour_boundary.json"),
            os.path.join(base_path, "player/contracts/onboarding_contract.json"),
        )
        self.mfm = MovementFeelManager(
            os.path.join(base_path, "traversal/contracts/traversal_boundary.json"),
            os.path.join(base_path, "traversal/contracts/movement_contract_schema.json"),
        )
        self.cfm = CombatFeelManager(
            os.path.join(base_path, "combat/contracts/combat_feel_boundary.json"),
            os.path.join(base_path, "combat/contracts/combat_feedback_contract.json"),
        )
        self.eem = EnemyEcologyManager(
            os.path.join(base_path, "enemies/contracts/enemy_ecology_boundary.json"),
            os.path.join(base_path, "enemies/contracts/enemy_behavior_contract.json"),
        )
        self.sem = SurvivalEconomyManager(
            os.path.join(base_path, "economy/contracts/resource_scarcity_boundary.json"),
            os.path.join(base_path, "economy/contracts/survival_economy_contract.json"),
        )
        self.cm = ContinuationManager(
            os.path.join(base_path, "player/contracts/death_continuation_boundary.json"),
            os.path.join(base_path, "player/contracts/survivor_continuation_contract.json"),
        )
        self.vsm = VisualScaffoldManager(
            os.path.join(base_path, "presentation/visual_presentation_contract.json"),
            os.path.join(base_path, "presentation/hud_profile.json"),
            os.path.join(base_path, "presentation/placeholder_asset_manifest.json"),
        )

        # STAGE-069 runtime layering planner loads from TOWER_DATA only
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        tower_data_root = os.environ.get("TOWER_DATA_PATH") or os.path.join(project_root, "tower_data")
        self.apm = AudioPressureManager(
            tower_data_root=tower_data_root,
            runtime_contract_path=os.path.join(base_path, "audio/audio_runtime_contract.json"),
            mix_profiles_path=os.path.join(base_path, "audio/audio_mix_profiles.json"),
            event_map_path=os.path.join(base_path, "audio/audio_event_map.json"),
        )

        self.visual_log = []
        self.audio_log = []  # stores per-step audio plan dicts

    def _log_audit(self, event, details, audio_events=None):
        audio_events = audio_events or []
        self.audits.append({"timestamp": time.time(), "event": event, "details": details})

        # Generate audio plan driven by gameplay state + explicit events.
        audio_plan = self.apm.plan_audio_state(self.state, events=audio_events)
        self.audio_log.append(audio_plan)
        self.state["audio_plan"] = audio_plan

        # HUD-friendly summary string
        pressure_state = audio_plan.get("pressure_state", "unknown")
        mix = audio_plan.get("mix", {})
        amb_v = float(mix.get("base_ambience", {}).get("volume", 0.0))
        prs_v = float(mix.get("pressure", {}).get("volume", 0.0))
        ev_ct = sum(len(mix.get(k, {}).get("assets", [])) for k in ["movement", "interaction", "combat", "ui"])
        warn_ct = len(audio_plan.get("warnings", []) or [])
        self.state["audio_state"] = f"{pressure_state} amb={amb_v:.2f} pressure={prs_v:.2f} events={ev_ct} warnings={warn_ct}"

        # Generate and log visual state after each action
        self.visual_log.append(self.vsm.get_full_presentation(self.state, self.audits, self.state.get("recovery_manifest")))

    def simulate_player_input(self, action, value=None):
        self._log_audit("PLAYER_INPUT", {"action": action, "value": value})

        if action == "MOVE":
            return self._simulate_movement(value)
        if action == "ATTACK":
            return self._simulate_combat(value)
        if action == "PICKUP":
            return self._simulate_resource_pickup(value)
        if action == "USE_RESOURCE":
            return self._simulate_resource_use(value)
        if action == "TAKE_DAMAGE":
            return self._simulate_damage(value)
        if action == "DOOR":
            return self._simulate_door_interaction(value)
        if action == "UI_WARNING":
            self._log_audit("UI_WARNING", {"reason": value or ""}, audio_events=[{"type": "UI_WARNING", "id": str(value or "warning") }])
            return {"status": "WARNED"}

        return {"status": "UNKNOWN_ACTION"}

    def _simulate_movement(self, direction):
        mode = "STANDARD"
        if self.state["stamina"] < 20:
            mode = "INJURED"

        profile = self.mfm.generate_movement_profile(mode, self.state["pressure"], 100 - self.state["stamina"])
        self.state["stamina"] = max(0, self.state["stamina"] - 5)
        self.state["pressure"] = min(100, self.state["pressure"] + 2)
        self.state["location"] = f"Moved to {direction}"

        audio_events = [{"type": "MOVE_FOOTSTEP", "id": profile["movement_profile_id"]}]

        # Breathing intensity becomes pressure layer (procedural pressure layering)
        if float(profile["audio_feedback_profile"].get("breathing_intensity", 0.0)) >= 0.7:
            audio_events.append({"type": "PLAYER_BREATHING_INTENSE", "id": profile["movement_profile_id"]})

        # Occasional door interaction during traversal
        if random.random() < 0.25:
            door_res = self._simulate_door_interaction("OPEN", log_input=False)
            audio_events.extend(door_res.get("audio_events", []))

        self._log_audit(
            "MOVEMENT",
            {"profile": profile["movement_profile_id"], "location": self.state["location"], "mode": mode},
            audio_events=audio_events,
        )
        return {"status": "MOVED", "profile": profile}

    def _simulate_door_interaction(self, door_action, log_input=True):
        # door_action: OPEN|CLOSE|UNLOCK
        action = str(door_action or "OPEN").upper()
        if log_input:
            self._log_audit("PLAYER_INPUT", {"action": "DOOR", "value": action})

        etype = "INTERACT_DOOR_OPEN"
        if action == "CLOSE":
            etype = "INTERACT_DOOR_CLOSE"
        elif action == "UNLOCK":
            etype = "INTERACT_UNLOCK"

        audio_events = [{"type": etype, "id": f"door_{action.lower()}_{int(time.time()*1000)}"}]
        self._log_audit("DOOR_INTERACTION", {"action": action}, audio_events=audio_events)
        return {"status": "OK", "audio_events": audio_events}

    def _simulate_combat(self, enemy_type):
        enemy_profile = self.eem.generate_enemy_profile(enemy_type, self.state["pressure"], 50)

        damage = random.randint(10, 30)
        feedback = self.cfm.generate_hit_feedback("PLAYER_HIT_ENEMY", damage, self.state["pressure"])
        self.state["pressure"] = min(100, self.state["pressure"] + 10)

        audio_events = [{"type": "COMBAT_HIT", "id": feedback["feedback_id"]}]

        # Enemy proximity -> pressure cue
        if str(feedback["audio_feedback_profile"].get("threat_cue", "")).upper() == "HIGH":
            audio_events.append({"type": "ENEMY_PROXIMITY_CLOSE", "id": enemy_profile["enemy_profile_id"]})

        # Pressure escalation cue
        if self.state["pressure"] >= 60:
            audio_events.append({"type": "PRESSURE_ESCALATION", "id": f"pressure_{self.state['pressure']}"})

        self._log_audit(
            "COMBAT",
            {"enemy": enemy_profile["enemy_profile_id"], "feedback": feedback["feedback_id"], "damage": damage},
            audio_events=audio_events,
        )
        return {"status": "ENEMY_HIT", "damage_dealt": damage, "feedback": feedback}

    def _simulate_damage(self, amount):
        self.state["health"] -= int(amount or 0)

        audio_events = []
        if self.state["health"] <= 20:
            audio_events.append({"type": "UI_WARNING", "id": "low_health"})
        if self.state["pressure"] >= 80:
            audio_events.append({"type": "UI_WARNING", "id": "critical_pressure"})

        self._log_audit("TAKE_DAMAGE", {"amount": amount, "current_health": self.state["health"]}, audio_events=audio_events)

        if self.state["health"] <= 0:
            return self._trigger_death_event()
        return {"status": "DAMAGED", "health_remaining": self.state["health"]}

    def _simulate_resource_pickup(self, resource_type):
        profile = self.sem.generate_resource_profile(resource_type, random.randint(1, 10), self.state["pressure"])
        self.state["resources"][resource_type] = self.state["resources"].get(resource_type, 0) + 10
        self._log_audit("RESOURCE_PICKUP", {"type": resource_type, "profile": profile["resource_profile_id"]})
        return {"status": "PICKED_UP", "resource": resource_type}

    def _simulate_resource_use(self, resource_type):
        if self.state["resources"].get(resource_type, 0) > 0:
            self.state["resources"][resource_type] -= 1
            if resource_type == "FOOD":
                self.state["health"] = min(100, self.state["health"] + 10)
            self._log_audit("RESOURCE_USE", {"type": resource_type})
            return {"status": "USED", "resource": resource_type}
        return {"status": "NO_RESOURCE", "resource": resource_type}

    def _trigger_death_event(self):
        self.state["has_died"] = True
        death_id = f"death_{self.state['play_session_id']}"
        self._log_audit(
            "DEATH_EVENT",
            {"survivor_id": self.state["survivor_id"], "context": "ZERO_HEALTH"},
            audio_events=[{"type": "DEATH_EVENT", "id": death_id}],
        )

        manifest = self.cm.generate_continuation_manifest(self.state["survivor_id"], death_id, "ZERO_HEALTH")
        self.state["recovery_manifest"] = manifest

        self._log_audit("CONTINUATION_MANIFEST", {"manifest_id": manifest["continuation_id"]})
        return {"status": "DEFEATED", "manifest_id": manifest["continuation_id"]}

    def simulate_recovery(self):
        if (not self.state["has_died"]) or (not self.state.get("recovery_manifest")):
            return {"status": "NO_DEFEAT_TO_RECOVER"}

        recovery_report = self.cm.resolve_legacy_recovery(self.state["recovery_manifest"], "RECOVERY_RUN")

        self.state["health"] = 50
        self.state["stamina"] = 50
        self.state["pressure"] = 10
        self.state["has_died"] = False
        self.state["location"] = "Recovery Zone"
        self.state["recover_status"] = recovery_report["status"]
        del self.state["recovery_manifest"]

        self._log_audit(
            "RECOVERY",
            {"report": recovery_report["status"]},
            audio_events=[{"type": "RECOVERY_EVENT", "id": f"recovery_{int(time.time())}"}],
        )
        return {"status": "RECOVERED", "details": recovery_report}

    def run_playable_loop(self):
        self._log_audit("PLAY_LOOP_START", {"session": self.state["play_session_id"]})

        onboarding_profile = self.om.generate_onboarding_profile(self.state["survivor_id"])
        self.om.advance_onboarding(onboarding_profile, "FIRST_MOVEMENT")
        self._log_audit("ONBOARDING_INITIALIZED", {"profile_id": onboarding_profile["onboarding_profile_id"]})

        for _ in range(3):
            if self.state["health"] <= 0:
                break
            self.simulate_player_input("MOVE", random.choice(["NORTH", "EAST", "SOUTH", "WEST"]))
            if random.random() < 0.7:
                self.simulate_player_input("ATTACK", random.choice(["PREDATOR", "SCAVENGER"]))
                self.simulate_player_input("TAKE_DAMAGE", random.randint(5, 25))
            if random.random() < 0.5:
                self.simulate_player_input("PICKUP", random.choice(["FOOD", "SCRAP"]))
            if self.state["health"] < 70 and self.state["resources"].get("FOOD", 0) > 0:
                self.simulate_player_input("USE_RESOURCE", "FOOD")

        if self.state["health"] > 0:
            self._simulate_damage(self.state["health"] + 10)

        if self.state["has_died"]:
            self.simulate_recovery()

        self._log_audit("PLAY_LOOP_END", {"final_state": self.state})

        return {
            "session_id": self.state["play_session_id"],
            "final_state": self.state,
            "audits": self.audits,
            "visual_log": self.visual_log,
            "audio_log": self.audio_log,
        }

    def get_audit_report(self):
        return {
            "session_id": self.state["play_session_id"],
            "audits": self.audits,
            "final_state": self.state,
            "visual_log": self.visual_log,
            "audio_log": self.audio_log,
        }


if __name__ == "__main__":
    os.makedirs("outputs/audits", exist_ok=True)

    # Minimal OS boundary stubs for testing
    minimal_terminal_boundary = {"audit_config": {"audit_log_path": "audit_log.jsonl"}}
    minimal_admin_contract = {"commands": [], "validation_rules": {"max_command_length": 256, "disallowed_characters": []}}

    os.makedirs("engine/os_boundary/contracts", exist_ok=True)

    terminal_boundary_path = "engine/os_boundary/contracts/restricted_terminal_boundary.json"
    admin_contract_path = "engine/os_boundary/contracts/admin_terminal_command_contract.json"

    if not os.path.exists(terminal_boundary_path):
        with open(terminal_boundary_path, "w", encoding="utf-8") as f:
            json.dump(minimal_terminal_boundary, f, indent=2)
    if not os.path.exists(admin_contract_path):
        with open(admin_contract_path, "w", encoding="utf-8") as f:
            json.dump(minimal_admin_contract, f, indent=2)

    psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
    session_report = psm.run_playable_loop()
    print(json.dumps(session_report, indent=2))
