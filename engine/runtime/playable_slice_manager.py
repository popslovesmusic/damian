import os
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
from engine.presentation.isometric_render_manager import IsometricRenderManager
from engine.presentation.visual_feedback_manager import VisualFeedbackManager
from engine.presentation.animation_manager import AnimationManager
from engine.presentation.lighting_manager import LightingManager
from engine.presentation.visual_asset_selection_manager import VisualAssetSelectionManager
from engine.presentation.graphics_performance_manager import GraphicsPerformanceManager
from engine.runtime.runtime_integration_auditor import RuntimeIntegrationAuditor
from engine.world.landmark_storytelling_manager import LandmarkStorytellingManager
from engine.world.room_dressing_manager import RoomDressingManager
from engine.presentation.room_identity_auditor import RoomIdentityAuditor
from engine.runtime.contact_boundary_manager import ContactBoundaryManager
from engine.runtime.combat_contact_manager import CombatContactManager
from engine.runtime.traversal_contact_manager import TraversalContactManager
from engine.runtime.hazard_contact_manager import HazardContactManager
from engine.runtime.interaction_object_manager import InteractionObjectManager
from engine.runtime.loot_resource_manager import LootResourceManager
from engine.runtime.inventory_manager import InventoryManager

# STAGE-069 runtime layering planner
from engine.audio.audio_pressure_manager import AudioPressureManager

# STAGE-070 enemy hunt + adaptation
from engine.enemy.enemy_hunt_manager import EnemyHuntManager

# STAGE-071 procedural floor + hazards
from engine.world.floor_generation_manager import FloorGenerationManager

# STAGE-072 world memory + survivor residue
from engine.world.world_memory_manager import WorldMemoryManager

# STAGE-073 async ghost presence
from engine.social.ghost_presence_manager import GhostPresenceManager

# STAGE-074 domain echo conflict
from engine.social.domain_echo_manager import DomainEchoManager

# STAGE-075 faction pressure
from engine.social.faction_pressure_manager import FactionPressureManager


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
        self.irm = IsometricRenderManager(
            os.path.join(base_path, "presentation/isometric_render_contract.json"),
            os.path.join(base_path, "presentation/visual_tile_rules.json"),
            os.path.join(base_path, "presentation/lighting_pressure_profile.json"),
            os.path.join(base_path, "presentation/fog_occlusion_rules.json"),
            os.path.join(base_path, "presentation/visual_asset_binding_manifest.json"),
            animation_manager=AnimationManager(
                os.path.join(base_path, "presentation/animation_contract.json"),
                os.path.join(base_path, "presentation/animation_state_profile.json"),
                os.path.join(base_path, "presentation/sprite_sheet_rules.json"),
                os.path.join(base_path, "presentation/enemy_animation_profile.json"),
            ),
            lighting_manager=LightingManager(
                os.path.join(base_path, "presentation/lighting_contract.json"),
                os.path.join(base_path, "presentation/fog_pressure_profile.json"),
                os.path.join(base_path, "presentation/occlusion_rules.json"),
                os.path.join(base_path, "presentation/danger_lighting_profile.json"),
            ),
            asset_selection_manager=VisualAssetSelectionManager(
                os.path.join(base_path, "presentation/visual_asset_selection_contract.json"),
                os.path.join(base_path, "presentation/approved_runtime_visual_set.json"),
                os.path.join(base_path, "presentation/rejected_visual_asset_log.json"),
                os.path.join(base_path, "presentation/visual_consistency_rules.json"),
            ),
            performance_manager=GraphicsPerformanceManager(
                os.path.join(base_path, "presentation/graphics_performance_contract.json"),
                os.path.join(base_path, "presentation/render_budget_profile.json"),
                os.path.join(base_path, "presentation/visual_readability_metrics.json"),
            ),
            fallback_profile_path=os.path.join(base_path, "runtime/runtime_fallback_profile.json"),
        )
        self.vfm = VisualFeedbackManager(
            os.path.join(base_path, "presentation/visual_feedback_contract.json"),
            os.path.join(base_path, "presentation/interaction_prompt_profile.json"),
            os.path.join(base_path, "presentation/hazard_visual_rules.json"),
            os.path.join(base_path, "presentation/residue_visual_rules.json"),
        )
        self.rdm = RoomDressingManager(
            os.path.join(base_path, "world/room_dressing_contract.json"),
            os.path.join(base_path, "world/prop_placement_rules.json"),
            os.path.join(base_path, "world/environment_clutter_profile.json"),
            os.path.join(base_path, "world/room_silhouette_profile.json"),
        )
        self.lsm = LandmarkStorytellingManager(
            os.path.join(base_path, "world/landmark_storytelling_contract.json"),
            os.path.join(base_path, "world/landmark_generation_rules.json"),
            os.path.join(base_path, "world/environmental_story_profile.json"),
            os.path.join(base_path, "world/faction_ruin_profile.json"),
            os.path.join(base_path, "world/ritual_space_profile.json"),
        )
        self.cbm = ContactBoundaryManager(
            os.path.join(base_path, "runtime/contact_boundary_contract.json"),
            os.path.join(base_path, "runtime/boundary_priority_rules.json"),
            os.path.join(base_path, "runtime/interaction_volume_profile.json"),
            os.path.join(base_path, "runtime/hazard_contact_profile.json"),
        )
        self.tcm = TraversalContactManager(
            os.path.join(base_path, "runtime/traversal_contact_contract.json"),
            os.path.join(base_path, "runtime/movement_resolution_rules.json"),
            os.path.join(base_path, "runtime/stamina_movement_profile.json"),
            os.path.join(base_path, "runtime/route_contact_profile.json"),
            self.cbm,
        )
        self.hcm = HazardContactManager(
            os.path.join(base_path, "runtime/hazard_contact_contract.json"),
            os.path.join(base_path, "runtime/hazard_damage_rules.json"),
            os.path.join(base_path, "runtime/environmental_damage_profile.json"),
            os.path.join(base_path, "runtime/hazard_warning_profile.json"),
            self.cbm,
        )
        self.lrm = LootResourceManager(
            os.path.join(base_path, "runtime/loot_resource_contract.json"),
            os.path.join(base_path, "runtime/resource_spawn_rules.json"),
            os.path.join(base_path, "runtime/resource_decay_rules.json"),
            os.path.join(base_path, "runtime/container_loot_profile.json"),
        )
        self.ccm = CombatContactManager(
            os.path.join(base_path, "runtime/combat_contact_contract.json"),
            os.path.join(base_path, "runtime/damage_resolution_rules.json"),
            os.path.join(base_path, "runtime/weapon_contact_profile.json"),
            os.path.join(base_path, "runtime/hurt_volume_profile.json"),
            self.cbm,
        )
        self.ria = RoomIdentityAuditor(
            os.path.join(base_path, "presentation/room_identity_contract.json"),
            os.path.join(base_path, "presentation/room_readability_rules.json"),
            os.path.join(base_path, "presentation/room_identity_score_profile.json"),
        )
        self.auditor = RuntimeIntegrationAuditor(self)

        # STAGE-072: world memory persistence rooted in project build/ (not TOWER_OS)
        self.wmm = None
        self._run_route_edges = []
        self._visited_rooms = []
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            data_root = os.path.join(project_root, "build/runtime_persistence_test")
            os.makedirs(data_root, exist_ok=True)
            self.wmm = WorldMemoryManager(
                os.path.join(base_path, "world/world_memory_contract.json"),
                os.path.join(base_path, "world/residue_rules.json"),
                os.path.join(base_path, "world/survivor_residue_profile.json"),
                data_root=data_root,
            )
            snap = self.wmm.snapshot()
            self.state["world_haunting_level"] = float(snap.get("haunting_level", 0.0) or 0.0)
            self.state["world_memory_summary"] = {
                "haunting_level": round(float(snap.get("haunting_level", 0.0) or 0.0), 3),
                "room_scars": len(snap.get("room_scars") or {}),
                "route_fear": len(snap.get("route_fear") or {}),
                "enemy_memory_bias": round(float(snap.get("enemy_memory_bias", 0.0) or 0.0), 3),
            }
        except Exception:
            self.wmm = None

        # STAGE-073: ghost presence (async-only, derived from world memory)
        self.gpm = None
        self._last_edge = None
        try:
            self.gpm = GhostPresenceManager(
                os.path.join(base_path, "social/ghost_presence_contract.json"),
                os.path.join(base_path, "social/ghost_signal_rules.json"),
                os.path.join(base_path, "social/ghost_echo_profile.json"),
            )
        except Exception:
            self.gpm = None

        # STAGE-074: domain echo manager
        self.dem = None
        try:
            self.dem = DomainEchoManager(
                os.path.join(base_path, "social/domain_echo_contract.json"),
                os.path.join(base_path, "social/domain_conflict_rules.json"),
                os.path.join(base_path, "social/domain_pressure_profile.json"),
            )
        except Exception:
            self.dem = None

        # STAGE-075: faction pressure manager
        self.fpm = None
        try:
            self.fpm = FactionPressureManager(
                os.path.join(base_path, "social/faction_pressure_contract.json"),
                os.path.join(base_path, "social/faction_behavior_profile.json"),
                os.path.join(base_path, "social/political_collapse_rules.json"),
                os.path.join(base_path, "social/faction_memory_manifest.json"),
            )
        except Exception:
            self.fpm = None

        # STAGE-071: floor generation manager
        self.fgm = None
        self.route_rules = {}
        try:
            self.fgm = FloorGenerationManager(
                os.path.join(base_path, "world/floor_generation_contract.json"),
                os.path.join(base_path, "world/hazard_generation_profile.json"),
                os.path.join(base_path, "world/route_pressure_rules.json"),
                seed_manifest_path=os.path.join(base_path, "world/floor_seed_manifest.json"),
                dressing_manager=self.rdm,
                landmark_manager=self.lsm,
            )
            self.route_rules = self.fgm.route_rules or {}
            seed = None
            tier = 1
            try:
                seed = (self.fgm.seed_manifest or {}).get("default_seed")
                tier = int((self.fgm.seed_manifest or {}).get("default_difficulty_tier", 1))
            except Exception:
                seed = None
                tier = 1
            floor = self.fgm.generate_floor(seed=seed, difficulty_tier=tier)
            if self.wmm:
                floor = self.fgm.apply_world_memory(floor, self.wmm.snapshot())
            self.state["floor"] = floor
            self.state["current_room_id"] = (floor.get("critical_path") or ["R001"])[0]
            self._visited_rooms = [self.state["current_room_id"]]
            self.state["location"] = f"Room {self.state['current_room_id']}"
            self.state["floor_summary"] = self.fgm.summarize_floor(floor, current_room_id=self.state["current_room_id"])
            if self.gpm:
                self.gpm.reset_floor_budget()
            if self.wmm and self.dem:
                exported = self.wmm.export_domain_echo(
                    os.path.join(base_path, "social/domain_echo_contract.json"),
                    os.path.join(base_path, "social/domain_conflict_rules.json"),
                    os.path.join(base_path, "social/domain_pressure_profile.json"),
                )
                self.state["domain_echo"] = self.dem.resolve_conflict(self.wmm.snapshot(), exported)
        except Exception:
            self.fgm = None
            self.route_rules = {}

        # STAGE-070 hunt manager (graceful degradation if missing)
        self.ehm = None
        try:
            self.ehm = EnemyHuntManager(
                os.path.join(base_path, "enemy/enemy_hunt_contract.json"),
                os.path.join(base_path, "enemy/enemy_adaptation_profile.json"),
                os.path.join(base_path, "enemy/enemy_memory_rules.json"),
            )
        except Exception:
            self.ehm = None

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

    def _get_room(self, room_id):
        floor = self.state.get("floor") or {}
        for r in floor.get("rooms") or []:
            if r.get("room_id") == room_id:
                return r
        return None

    def _get_out_edges(self, room_id):
        floor = self.state.get("floor") or {}
        return [e for e in (floor.get("edges") or []) if e.get("from") == room_id]

    def _enter_room_effects(self, room):
        """
        Apply bounded room effects (pressure zones + hazards) and return audio_events.
        """
        audio_events = []
        if not room:
            return {"audio_events": audio_events}

        # STAGE-085: audit room visual identity
        if self.ria:
            audit_result = self.ria.audit_room(room)
            if audit_result["status"] == "FAIL":
                self._log_audit("ROOM_IDENTITY_FAIL", {"room_id": room.get("room_id"), "score": audit_result["score"]})

        # Pressure zone -> pressure delta + audio hook
        try:
            zone = room.get("pressure_level")
            rules = self.route_rules or {}
            delta = int((rules.get("pressure_zone_to_delta") or {}).get(zone, 0))
            self.state["pressure"] = int(max(0, min(100, int(self.state.get("pressure", 0)) + delta)))
            etype = (rules.get("pressure_zone_to_audio_event") or {}).get(zone)
            if etype:
                audio_events.append({"type": etype, "id": f"{room.get('room_id')}_{zone}"})
        except Exception:
            pass

        # STAGE-072: memory pressure bump (bounded), attached as metadata by floor memory application.
        try:
            mpb = int(room.get("memory_pressure_bump", 0) or 0)
            if mpb:
                self.state["pressure"] = int(max(0, min(100, int(self.state.get("pressure", 0)) + mpb)))
        except Exception:
            pass

        # Resource rooms grant modest, auditable pickups (won't trivialize survival).
        try:
            for res in list(room.get("resources") or []):
                prof = self.sem.generate_resource_profile(res, scarcity_level=7, world_pressure=int(self.state.get("pressure", 0)))
                self.state["resources"][res] = int(self.state["resources"].get(res, 0)) + 1
                self._log_audit("ROOM_RESOURCE", {"room_id": room.get("room_id"), "resource": res, "profile": prof.get("resource_profile_id")})
        except Exception:
            pass

        # Hazards -> bounded damage/pressure/noise
        if self.fgm:
            hz = self.fgm.evaluate_room_hazards(
                seed=str((self.state.get("floor") or {}).get("seed", "")),
                room_id=str(room.get("room_id")),
                hazards=list(room.get("hazards") or []),
                difficulty_tier=int((self.state.get("floor") or {}).get("difficulty_tier", 1)),
            )
            if hz.get("pressure_gain"):
                self.state["pressure"] = int(max(0, min(100, int(self.state.get("pressure", 0)) + int(hz["pressure_gain"]))))
            if hz.get("damage"):
                self.state["health"] = int(self.state.get("health", 0)) - int(hz["damage"])
            # Feed hazard noise into enemy hunt
            try:
                hunt = self._enemy_hunt_step(
                    signals={
                        "noise_level": float(hz.get("noise_gain", 0.0)),
                        "distance_m": 9.0,
                        "navigation_influence": float(room.get("enemy_influence", 0.0)),
                    }
                )
                audio_events.extend(hunt.get("audio_events", []))
            except Exception:
                pass

            self._log_audit("ROOM_EFFECTS", {"room_id": room.get("room_id"), "hazards": hz}, audio_events=audio_events)

            # STAGE-072: hazard triggers become residue
            try:
                if self.wmm:
                    for h in list((hz.get("hazards") or [])):
                        self.wmm.record_hazard_triggered(str(room.get("room_id")), str(h.get("type")))
            except Exception:
                pass

            if int(self.state.get("health", 0)) <= 0 and not self.state.get("has_died"):
                return {"audio_events": audio_events, "death": self._trigger_death_event()}

        # STAGE-073: ghost presence signals (async, bounded) on room entry
        try:
            if self.gpm and self.wmm:
                wm = self.wmm.snapshot()
                ghost = self.gpm.generate_signals(
                    world_memory=wm,
                    game_state=self.state,
                    floor=self.state.get("floor"),
                    current_room_id=self.state.get("current_room_id"),
                    last_edge=self._last_edge,
                )
                self.state["ghost_presence"] = ghost.get("summary")
                self.state["ghost_signals"] = ghost.get("signals")
                # Feed audio events
                audio_events.extend(ghost.get("audio_events") or [])
                # HUD extra lines
                if ghost.get("hud_lines"):
                    self.state["ghost_hud_lines"] = ghost.get("hud_lines")
                self._log_audit("GHOST_PRESENCE", {"summary": ghost.get("summary"), "signals": ghost.get("signals")}, audio_events=ghost.get("audio_events"))
        except Exception:
            pass

        # STAGE-074: apply imported echo pressure bump (bounded, never blocks solvability)
        try:
            echo = self.state.get("domain_echo")
            if isinstance(echo, dict):
                bump = int(echo.get("imported_pressure_bump", 0) or 0)
                if bump:
                    self.state["pressure"] = int(max(0, min(100, int(self.state.get("pressure", 0)) + bump)))
                    et_map = {
                        "passive_echo": "DOMAIN_ECHO_EVENT",
                        "challenge_echo": "DOMAIN_ECHO_CHALLENGE",
                        "invasion_echo": "DOMAIN_ECHO_INVASION",
                        "defense_echo": "DOMAIN_ECHO_DEFENSE",
                    }
                    etype = et_map.get(str(echo.get("mode")))
                    if etype:
                        audio_events.append({"type": etype, "id": f"{self.state.get('current_room_id')}_{echo.get('mode')}"})
                    if str(echo.get("mode")) == "challenge_echo" and self.state.get("floor"):
                        self.state["floor"].setdefault("optional_branches", [])
                        if not any(b.get("source") == "domain_echo" for b in self.state["floor"]["optional_branches"]):
                            self.state["floor"]["optional_branches"].append(
                                {
                                    "source": "domain_echo",
                                    "route_type": "challenge_echo",
                                    "hint": (echo.get("escape_signatures") or ["unknown"])[0],
                                    "reward_gate": True,
                                }
                            )
        except Exception:
            pass

        # STAGE-075: faction pressure (bounded) + persistent political memory
        try:
            if self.fpm and self.wmm:
                wm = self.wmm.snapshot()
                fac = self.fpm.step(
                    world_memory=wm,
                    game_state=self.state,
                    floor=self.state.get("floor"),
                    current_room=room,
                    domain_echo=self.state.get("domain_echo"),
                )
                self.state["faction_state"] = fac.get("faction_state")
                self.state["faction_pressure_level"] = float(fac.get("faction_pressure_level", 0.0) or 0.0)
                self.state["faction_hud_lines"] = fac.get("hud_lines") or []

                bump = int(fac.get("pressure_bump", 0) or 0)
                if bump:
                    self.state["pressure"] = int(max(0, min(100, int(self.state.get("pressure", 0)) + bump)))
                audio_events.extend(fac.get("audio_events") or [])

                # Persist into world memory (ruins/events)
                self.wmm.apply_faction_update(fac.get("faction_state") or {}, political_event=fac.get("political_event"))
                self._log_audit(
                    "FACTION_PRESSURE",
                    {"faction": fac.get("faction_state"), "political_event": fac.get("political_event")},
                    audio_events=fac.get("audio_events"),
                )
        except Exception:
            pass

        return {"audio_events": audio_events}

    def _enemy_hunt_step(self, signals, tactic=None):
        if not self.ehm:
            return {"audio_events": [], "hunt_state": "unknown", "hud_warning": None}

        if tactic:
            try:
                self.ehm.record_tactic(tactic)
            except Exception:
                pass

        signals = dict(signals or {})
        if self.wmm:
            try:
                signals["memory_bias"] = float(self.wmm.snapshot().get("enemy_memory_bias", 0.0) or 0.0)
            except Exception:
                pass
        if isinstance(self.state.get("domain_echo"), dict):
            try:
                signals["echo_enemy_bias"] = float(self.state["domain_echo"].get("echo_enemy_bias", 0.0) or 0.0)
            except Exception:
                pass
        if isinstance(self.state.get("faction_state"), dict):
            try:
                signals["faction_hostility"] = float(self.state["faction_state"].get("hostility_bias", 0.0) or 0.0)
            except Exception:
                pass
        res = self.ehm.step("enemy_0", self.state, signals=signals)
        self.state["enemy_hunt_state"] = res.get("state", "unknown")
        self.state["enemy_hunt_warning"] = res.get("hud_warning")
        self.state["enemy_adaptation_modifiers"] = res.get("modifiers", {})
        self.state["enemy_session_memory"] = res.get("memory", {})
        return {
            "audio_events": res.get("audio_events", []) or [],
            "hunt_state": self.state["enemy_hunt_state"],
            "hud_warning": self.state.get("enemy_hunt_warning"),
        }

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
        feedback = self.vfm.generate_feedback(self.state)
        anim_state = self.irm.animation_manager.get_animation_state("player", self.state)
        
        # Reset performance manager per audit step (which is per frame)
        if self.irm.performance_manager:
            self.irm.performance_manager.reset_frame_usage()
            
        self.visual_log.append({
            "scaffold": self.vsm.get_full_presentation(self.state, self.audits, self.state.get("recovery_manifest")),
            "isometric": self.irm.get_full_isometric_frame(self.state, feedback_layers=feedback.get("layers"), animation_state=anim_state)
        })

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

        # STAGE-071: movement chooses a graph edge when a floor is present.
        if self.state.get("floor") and self.state.get("current_room_id"):
            cur = self.state["current_room_id"]
            out_edges = self._get_out_edges(cur)
            if out_edges:
                # prefer main routes unless direction explicitly asks for RISK
                prefer_risk = str(direction or "").upper() in ("RISK", "BRANCH")
                main = [e for e in out_edges if e.get("route_type") == "main"]
                non_main = [e for e in out_edges if e.get("route_type") != "main"]
                chosen = (non_main[0] if (prefer_risk and non_main) else (main[0] if main else out_edges[0]))
                self.state["current_room_id"] = chosen["to"]
                self.state["location"] = f"Room {self.state['current_room_id']}"
                self._run_route_edges.append({"from": chosen.get("from"), "to": chosen.get("to"), "route_type": chosen.get("route_type")})
                self._visited_rooms.append(self.state["current_room_id"])
                self._last_edge = {"from": chosen.get("from"), "to": chosen.get("to"), "route_type": chosen.get("route_type")}
                # Edge costs
                self.state["stamina"] = max(0, int(self.state["stamina"]) - int(chosen.get("stamina_cost", 1)))
                
                # STAGE-089: resolve hazard contact
                hazard_effect = self.hcm.resolve_hazard(self.state["current_room_id"], {"x": 0, "y": 0})
                if hazard_effect:
                    self.state["health"] = max(0, self.state["health"] - hazard_effect["damage"])
                    self.state["pressure"] = min(100, self.state["pressure"] + hazard_effect["pressure"])
                    audio_events.append({"type": hazard_effect["event"], "id": f"{self.state['current_room_id']}_hazard"})

                try:
                    bias = (self.route_rules.get("route_type_bias") or {}).get(chosen.get("route_type")) or {}
                    self.state["pressure"] = min(100, int(self.state["pressure"]) + int(bias.get("pressure_delta", 0)))
                except Exception:
                    pass
                # Update summaries
                if self.fgm:
                    self.state["floor_summary"] = self.fgm.summarize_floor(self.state["floor"], current_room_id=self.state["current_room_id"])
                # Apply room entry effects
                room = self._get_room(self.state["current_room_id"])
                try:
                    if self.wmm and room:
                        self.wmm.record_room_visit(str(room.get("room_id")))
                except Exception:
                    pass
                self._enter_room_effects(room)

        profile = self.mfm.generate_movement_profile(mode, self.state["pressure"], 100 - self.state["stamina"])
        self.state["stamina"] = max(0, self.state["stamina"] - 5)
        self.state["pressure"] = min(100, self.state["pressure"] + 2)
        if not self.state.get("floor"):
            self.state["location"] = f"Moved to {direction}"

        audio_events = [{"type": "MOVE_FOOTSTEP", "id": profile["movement_profile_id"]}]

        # Breathing intensity becomes pressure layer (procedural pressure layering)
        if float(profile["audio_feedback_profile"].get("breathing_intensity", 0.0)) >= 0.7:
            audio_events.append({"type": "PLAYER_BREATHING_INTENSE", "id": profile["movement_profile_id"]})

        # Occasional door interaction during traversal
        if random.random() < 0.25:
            door_res = self._simulate_door_interaction("OPEN", log_input=False)
            audio_events.extend(door_res.get("audio_events", []))

        # STAGE-070: movement noise can trigger suspicion/tracking
        nav_influence = 0.0
        try:
            room = self._get_room(self.state.get("current_room_id"))
            nav_influence = float((room or {}).get("enemy_influence", 0.0))
        except Exception:
            nav_influence = 0.0
        hunt = self._enemy_hunt_step(
            signals={"noise_level": 0.55 if mode == "STANDARD" else 0.35, "distance_m": 10.0, "navigation_influence": nav_influence},
            tactic="RUN",
        )
        audio_events.extend(hunt.get("audio_events", []))

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

        # STAGE-070: door use reinforces local checks without omniscience
        hunt = self._enemy_hunt_step(signals={"door_event": True, "noise_level": 0.4, "distance_m": 8.0}, tactic="DOOR")
        audio_events.extend(hunt.get("audio_events", []))
        try:
            if self.wmm:
                self.wmm.record_door_usage()
        except Exception:
            pass

        self._log_audit("DOOR_INTERACTION", {"action": action}, audio_events=audio_events)
        return {"status": "OK", "audio_events": audio_events}

    def _simulate_combat(self, enemy_type):
        enemy_profile = self.eem.generate_enemy_profile(enemy_type, self.state["pressure"], 50)

        damage = self.ccm.resolve_attack("player", "enemy_0", self.state["current_room_id"], "sword")
        if damage is None:
            return {"status": "MISSED"}

        feedback = self.cfm.generate_hit_feedback("PLAYER_HIT_ENEMY", damage, self.state["pressure"])
        self.state["pressure"] = min(100, self.state["pressure"] + 10)

        audio_events = [{"type": "COMBAT_HIT", "id": feedback["feedback_id"]}]

        # Enemy proximity -> pressure cue
        if str(feedback["audio_feedback_profile"].get("threat_cue", "")).upper() == "HIGH":
            audio_events.append({"type": "ENEMY_PROXIMITY_CLOSE", "id": enemy_profile["enemy_profile_id"]})

        # Pressure escalation cue
        if self.state["pressure"] >= 60:
            audio_events.append({"type": "PRESSURE_ESCALATION", "id": f"pressure_{self.state['pressure']}"})

        # STAGE-070: combat and proximity can push into hunting/attacking
        hunt = self._enemy_hunt_step(
            signals={"combat_event": True, "noise_level": 0.7, "distance_m": 2.0},
            tactic="ATTACK",
        )
        audio_events.extend(hunt.get("audio_events", []))
        try:
            if self.wmm:
                self.wmm.record_combat_pattern()
        except Exception:
            pass

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

        # STAGE-070: getting hurt increases pressure and can sustain pursuit without omniscience
        hunt = self._enemy_hunt_step(signals={"noise_level": 0.25, "distance_m": 4.0})
        audio_events.extend(hunt.get("audio_events", []))

        self._log_audit(
            "TAKE_DAMAGE",
            {"amount": amount, "current_health": self.state["health"], "enemy_hunt_state": self.state.get("enemy_hunt_state")},
            audio_events=audio_events,
        )

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

        # STAGE-072: write death residue into world memory
        try:
            if self.wmm:
                floor_id = str((self.state.get("floor") or {}).get("floor_id", ""))
                room_id = self.state.get("current_room_id")
                self.wmm.record_death(floor_id=floor_id, room_id=room_id)
        except Exception:
            pass

        # STAGE-070: record encounter residue into audits (bounded, local, no OS writes)
        try:
            if self.ehm:
                self.ehm.record_tactic("DEATH")
                self.state["encounter_residue"] = self.ehm.snapshot()
        except Exception:
            pass

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

        # STAGE-070: post-recovery starts less immediately aggressive (bounded)
        try:
            if self.ehm:
                self.ehm.record_tactic("DEATH", intensity=0.0)
                self._enemy_hunt_step(signals={"noise_level": 0.0})
        except Exception:
            pass

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

        # STAGE-072: route memory on escape (end-of-run)
        try:
            if self.wmm:
                self.wmm.record_escape_route(self._run_route_edges, room_path=self._visited_rooms)
        except Exception:
            pass

        # STAGE-072: if we survived critical health, leave a subtle echo marker
        try:
            if self.wmm and int(self.state.get("health", 0)) > 0 and int(self.state.get("health", 0)) <= 20:
                self.wmm.record_critical_survival()
        except Exception:
            pass

        # Persist world memory and write an auditable Stage-072 snapshot
        try:
            if self.wmm:
                mem_path = self.wmm.save()
                snap = self.wmm.snapshot()
                self.state["world_haunting_level"] = float(snap.get("haunting_level", 0.0) or 0.0)
                self.state["world_memory_summary"] = {
                    "haunting_level": round(float(snap.get("haunting_level", 0.0) or 0.0), 3),
                    "room_scars": len(snap.get("room_scars") or {}),
                    "route_fear": len(snap.get("route_fear") or {}),
                    "enemy_memory_bias": round(float(snap.get("enemy_memory_bias", 0.0) or 0.0), 3),
                    "path": mem_path,
                }
                if self.gpm:
                    self.state["ghost_presence"] = self.state.get("ghost_presence") or {"haunting_level": self.state.get("world_haunting_level"), "emitted": 0}
                os.makedirs("outputs/audits", exist_ok=True)
                with open("outputs/audits/stage_072_survivor_residue_world_memory_audit.json", "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "stage_id": "STAGE-072",
                            "patch_id": "STAGE-072-SURVIVOR-RESIDUE-WORLD-MEMORY-001",
                            "verdict": "PENDING",
                            "final_state": self.state,
                            "world_memory": snap,
                        },
                        f,
                        indent=2,
                    )
        except Exception:
            pass

        # STAGE-073: write ghost presence audit (async-only)
        try:
            os.makedirs("outputs/audits", exist_ok=True)
            with open("outputs/audits/stage_073_async_ghost_presence_audit.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "stage_id": "STAGE-073",
                        "patch_id": "STAGE-073-ASYNC-GHOST-PRESENCE-RUNTIME-001",
                        "verdict": "PENDING",
                        "ghost_summary": self.state.get("ghost_presence"),
                        "ghost_signals": self.state.get("ghost_signals") or [],
                        "world_haunting_level": self.state.get("world_haunting_level"),
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

        # STAGE-074: write domain echo conflict audit
        try:
            os.makedirs("outputs/audits", exist_ok=True)
            with open("outputs/audits/stage_074_domain_echo_conflict_audit.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "stage_id": "STAGE-074",
                        "patch_id": "STAGE-074-DOMAIN-ECHO-CONFLICT-RUNTIME-001",
                        "verdict": "PENDING",
                        "domain_echo": self.state.get("domain_echo"),
                        "world_haunting_level": self.state.get("world_haunting_level"),
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

        # STAGE-075: write faction pressure audit
        try:
            os.makedirs("outputs/audits", exist_ok=True)
            with open("outputs/audits/stage_075_faction_pressure_review_audit.json", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "stage_id": "STAGE-075",
                        "patch_id": "STAGE-075-FACTION-PRESSURE-POLITICAL-COLLAPSE-001",
                        "verdict": "PENDING",
                        "faction_state": self.state.get("faction_state"),
                        "faction_pressure_level": self.state.get("faction_pressure_level"),
                        "world_memory": (self.wmm.snapshot() if self.wmm else None),
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

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
