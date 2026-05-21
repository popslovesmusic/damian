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

class PlayableSliceManager:
    def __init__(self, contract_path):
        with open(contract_path, 'r') as f:
            self.contract = json.load(f)

        self.audits = []
        self.state = {
            "survivor_id": "TEST_SURVIVOR",
            "health": 100,
            "stamina": 100,
            "resources": {"FOOD": 50, "WATER": 50, "SCRAP": 20},
            "location": "Starting Zone",
            "pressure": 0,
            "has_died": False,
            "play_session_id": f"PS_{int(time.time())}"
        }

        # Initialize sub-managers (simplified pathing for prototype)
        base_path = "engine/"
        self.om = OnboardingManager(
            os.path.join(base_path, "player/contracts/first_hour_boundary.json"),
            os.path.join(base_path, "player/contracts/onboarding_contract.json")
        )
        self.mfm = MovementFeelManager(
            os.path.join(base_path, "traversal/contracts/traversal_boundary.json"),
            os.path.join(base_path, "traversal/contracts/movement_contract_schema.json")
        )
        self.cfm = CombatFeelManager(
            os.path.join(base_path, "combat/contracts/combat_feel_boundary.json"),
            os.path.join(base_path, "combat/contracts/combat_feedback_contract.json")
        )
        self.eem = EnemyEcologyManager(
            os.path.join(base_path, "enemies/contracts/enemy_ecology_boundary.json"),
            os.path.join(base_path, "enemies/contracts/enemy_behavior_contract.json")
        )
        self.sem = SurvivalEconomyManager(
            os.path.join(base_path, "economy/contracts/resource_scarcity_boundary.json"),
            os.path.join(base_path, "economy/contracts/survival_economy_contract.json")
        )
        self.cm = ContinuationManager(
            os.path.join(base_path, "player/contracts/death_continuation_boundary.json"),
            os.path.join(base_path, "player/contracts/survivor_continuation_contract.json")
        )

    def _log_audit(self, event, details):
        self.audits.append({"timestamp": time.time(), "event": event, "details": details})

    def simulate_player_input(self, action, value=None):
        """Simulates basic player actions."""
        self._log_audit("PLAYER_INPUT", {"action": action, "value": value})
        
        if action == "MOVE":
            return self._simulate_movement(value)
        elif action == "ATTACK":
            return self._simulate_combat(value)
        elif action == "PICKUP":
            return self._simulate_resource_pickup(value)
        elif action == "USE_RESOURCE":
            return self._simulate_resource_use(value)
        elif action == "TAKE_DAMAGE":
            return self._simulate_damage(value)
        else:
            return {"status": "UNKNOWN_ACTION"}

    def _simulate_movement(self, direction):
        """Integrates movement_feel_manager."""
        mode = "STANDARD"
        if self.state["stamina"] < 20: mode = "INJURED"
        
        profile = self.mfm.generate_movement_profile(mode, self.state["pressure"], 100 - self.state["stamina"])
        self.state["stamina"] -= 5
        self.state["pressure"] = min(100, self.state["pressure"] + 2)
        self.state["location"] = f"Moved to {direction}"
        self._log_audit("MOVEMENT", {"profile": profile["movement_profile_id"], "location": self.state["location"]})
        return {"status": "MOVED", "profile": profile}

    def _simulate_combat(self, enemy_type):
        """Integrates combat_feel_manager and enemy_ecology_manager."""
        enemy_profile = self.eem.generate_enemy_profile(enemy_type, self.state["pressure"], 50) # Assuming route usage
        
        damage = random.randint(10, 30)
        feedback = self.cfm.generate_hit_feedback("PLAYER_HIT_ENEMY", damage, self.state["pressure"])
        self.state["pressure"] = min(100, self.state["pressure"] + 10)
        
        self._log_audit("COMBAT", {"enemy": enemy_profile["enemy_profile_id"], "feedback": feedback["feedback_id"]})
        return {"status": "ENEMY_HIT", "damage_dealt": damage, "feedback": feedback}

    def _simulate_damage(self, amount):
        """Simulates taking damage, potentially leading to death."""
        self.state["health"] -= amount
        self._log_audit("TAKE_DAMAGE", {"amount": amount, "current_health": self.state["health"]})

        if self.state["health"] <= 0:
            return self._trigger_death_event()
        return {"status": "DAMAGED", "health_remaining": self.state["health"]}

    def _simulate_resource_pickup(self, resource_type):
        """Integrates survival_economy_manager."""
        profile = self.sem.generate_resource_profile(resource_type, random.randint(1,10), self.state["pressure"])
        self.state["resources"][resource_type] = self.state["resources"].get(resource_type, 0) + 10
        self._log_audit("RESOURCE_PICKUP", {"type": resource_type, "profile": profile["resource_profile_id"]})
        return {"status": "PICKED_UP", "resource": resource_type}

    def _simulate_resource_use(self, resource_type):
        """Integrates survival_economy_manager (simplified use)."""
        if self.state["resources"].get(resource_type, 0) > 0:
            self.state["resources"][resource_type] -= 1
            if resource_type == "FOOD": self.state["health"] = min(100, self.state["health"] + 10)
            self._log_audit("RESOURCE_USE", {"type": resource_type})
            return {"status": "USED", "resource": resource_type}
        return {"status": "NO_RESOURCE", "resource": resource_type}

    def _trigger_death_event(self):
        """Integrates continuation_manager."""
        self.state["has_died"] = True
        self._log_audit("DEATH_EVENT", {"survivor_id": self.state["survivor_id"], "context": "ZERO_HEALTH"})
        
        manifest = self.cm.generate_continuation_manifest(
            self.state["survivor_id"], f"death_{self.state['play_session_id']}", "ZERO_HEALTH"
        )
        self.state["recovery_manifest"] = manifest
        
        self._log_audit("CONTINUATION_MANIFEST", {"manifest_id": manifest["continuation_id"]})
        return {"status": "DEFEATED", "manifest_id": manifest["continuation_id"]}

    def simulate_recovery(self):
        """Simulates recovery after death."""
        if not self.state["has_died"] or not self.state.get("recovery_manifest"):
            return {"status": "NO_DEFEAT_TO_RECOVER"}
        
        # Simulate selecting a recovery option
        recovery_report = self.cm.resolve_legacy_recovery(self.state["recovery_manifest"], "RECOVERY_RUN")
        
        # Reset state (simplified)
        self.state["health"] = 50
        self.state["stamina"] = 50
        self.state["pressure"] = 10
        self.state["has_died"] = False
        self.state["location"] = "Recovery Zone"
        del self.state["recovery_manifest"]
        
        self._log_audit("RECOVERY", {"report": recovery_report["status"]})
        return {"status": "RECOVERED", "details": recovery_report}

    def run_playable_loop(self):
        """Runs a full simulated playable loop: Onboarding -> Play -> Death -> Recovery."""
        self._log_audit("PLAY_LOOP_START", {"session": self.state["play_session_id"]})
        
        # 1. Onboarding
        onboarding_profile = self.om.generate_onboarding_profile(self.state["survivor_id"])
        self.om.advance_onboarding(onboarding_profile, "FIRST_MOVEMENT")
        self._log_audit("ONBOARDING_INITIALIZED", {"profile_id": onboarding_profile["onboarding_profile_id"]})

        # 2. Play Loop: Movement, Combat, Resource, Damage
        for i in range(3): # Simulate a few turns
            if self.state["health"] <= 0: break
            self.simulate_player_input("MOVE", random.choice(["NORTH", "EAST", "SOUTH", "WEST"]))
            if random.random() < 0.7: # Chance for combat
                self.simulate_player_input("ATTACK", random.choice(["PREDATOR", "SCAVENGER"]))
                self.simulate_player_input("TAKE_DAMAGE", random.randint(5, 25))
            if random.random() < 0.5: # Chance for resource
                self.simulate_player_input("PICKUP", random.choice(["FOOD", "SCRAP"]))
            if self.state["health"] < 70 and self.state["resources"].get("FOOD", 0) > 0:
                self.simulate_player_input("USE_RESOURCE", "FOOD")
        
        # Force a death event if not already dead
        if self.state["health"] > 0:
            self._simulate_damage(self.state["health"] + 10) # Overkill to ensure death
        
        # 3. Recovery
        if self.state["has_died"]:
            self.simulate_recovery()
        
        self._log_audit("PLAY_LOOP_END", {"final_state": self.state})
        
        return {"session_id": self.state["play_session_id"], "final_state": self.state, "audits": self.audits}

    def get_audit_report(self):
        """Returns the full audit log of the session."""
        return {"session_id": self.state["play_session_id"], "audits": self.audits, "final_state": self.state}

if __name__ == "__main__":
    # Ensure audit directory exists for sub-managers
    os.makedirs("outputs/audits", exist_ok=True)
    
    # Placeholder for restricted_terminal_boundary.json and admin_terminal_command_contract.json
    # These are needed for sub-managers but not directly for PlayableSliceManager's core loop
    # We'll create minimal versions if they don't exist for testing purposes.
    minimal_terminal_boundary = {
        "audit_config": {"audit_log_path": "audit_log.jsonl"}
    }
    minimal_admin_contract = {"commands": [], "validation_rules": {"max_command_length": 256, "disallowed_characters": []}}
    
    os.makedirs("engine/os_boundary/contracts", exist_ok=True)
    
    terminal_boundary_path = "engine/os_boundary/contracts/restricted_terminal_boundary.json"
    admin_contract_path = "engine/os_boundary/contracts/admin_terminal_command_contract.json"
    
    if not os.path.exists(terminal_boundary_path):
        with open(terminal_boundary_path, 'w') as f:
            json.dump(minimal_terminal_boundary, f, indent=2)
    if not os.path.exists(admin_contract_path):
        with open(admin_contract_path, 'w') as f:
            json.dump(minimal_admin_contract, f, indent=2)

    psm = PlayableSliceManager("engine/runtime/contracts/vertical_slice_contract.json")
    session_report = psm.run_playable_loop()
    print(json.dumps(session_report, indent=2))
