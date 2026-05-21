import json
import os
import random
import time
import hashlib
from collections import deque
from engine.world.room_dressing_manager import RoomDressingManager
from engine.world.landmark_storytelling_manager import LandmarkStorytellingManager

def _safe_load_json(path: str):

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def _stable_room_id(index: int):
    return f"R{index:03d}"


class FloorGenerationManager:
    """
    STAGE-071: Seed-reproducible, solvable floor topology with bounded hazards and auditable route risk.
    """

    def __init__(
        self,
        contract_path: str,
        hazard_profile_path: str,
        route_pressure_rules_path: str,
        seed_manifest_path: str | None = None,
        dressing_manager: RoomDressingManager | None = None,
        landmark_manager: LandmarkStorytellingManager | None = None,
    ):
        self.contract = _safe_load_json(contract_path)
        self.hazard_profile = _safe_load_json(hazard_profile_path)
        self.route_rules = _safe_load_json(route_pressure_rules_path)
        self.seed_manifest = _safe_load_json(seed_manifest_path) if seed_manifest_path else None
        self.dressing_manager = dressing_manager
        self.landmark_manager = landmark_manager

    def _rng(self, seed):
        if seed is None:
            seed = f"seed_{int(time.time())}"
        seed_str = str(seed)
        # Make RNG stable across Python runs by hashing seed string to int
        seed_int = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:16], 16)
        return random.Random(seed_int), seed_str

    def _choose_pressure_level(self, rng: random.Random, room_type: str):
        # Entry/exit are calmer on average; hazard/combat skew higher.
        if room_type == "entry":
            return rng.choices(["calm", "uneasy"], weights=[0.8, 0.2])[0]
        if room_type == "exit":
            return rng.choices(["uneasy", "hunted"], weights=[0.6, 0.4])[0]
        if room_type == "hazard":
            return rng.choices(["uneasy", "hunted", "critical"], weights=[0.35, 0.45, 0.2])[0]
        if room_type == "combat":
            return rng.choices(["uneasy", "hunted", "critical"], weights=[0.3, 0.5, 0.2])[0]
        if room_type == "false_safety":
            return rng.choices(["calm", "uneasy", "hunted"], weights=[0.5, 0.4, 0.1])[0]
        return rng.choices(["calm", "uneasy", "hunted"], weights=[0.3, 0.55, 0.15])[0]

    def _choose_room_audio_profile(self, pressure_level: str):
        if pressure_level in ("hunted", "critical"):
            return "pressure"
        return "ambience"

    def _hazard_tier_cfg(self, difficulty_tier: int):
        tiers = self.hazard_profile.get("difficulty_tiers") or {}
        return tiers.get(str(int(difficulty_tier))) or tiers.get("1") or {
            "max_hazards_per_room": 1,
            "hazard_chance": 0.3,
            "max_room_damage": 15,
            "max_room_pressure_gain": 12,
        }

    def _generate_room_hazards(self, rng: random.Random, room_type: str, difficulty_tier: int):
        if room_type in ("entry", "exit"):
            return []
        tier_cfg = self._hazard_tier_cfg(difficulty_tier)
        hazard_chance = float(tier_cfg.get("hazard_chance", 0.3))
        max_per = int(tier_cfg.get("max_hazards_per_room", 1))
        if rng.random() > hazard_chance:
            return []
        hz_types = list(self.hazard_profile.get("hazard_types") or [])
        rng.shuffle(hz_types)
        hazards = []
        for hz in hz_types:
            if len(hazards) >= max_per:
                break
            if room_type == "resource" and hz in ("corruption_pool",):
                continue
            hazards.append(hz)
            if rng.random() < 0.35:
                break
        return hazards

    def _generate_room_resources(self, rng: random.Random, room_type: str):
        if room_type != "resource":
            return []
        # Keep modest to avoid trivializing survival pressure.
        candidates = ["FOOD", "WATER", "SCRAP"]
        rng.shuffle(candidates)
        picked = candidates[: rng.choice([1, 2])]
        return picked

    def generate_floor(self, seed=None, difficulty_tier: int = 1):
        rng, seed_str = self._rng(seed)

        gen = self.contract.get("generation") or {}
        min_rooms = int(gen.get("min_rooms", 6))
        max_rooms = int(gen.get("max_rooms", 12))
        min_cp = int(gen.get("min_critical_path_rooms", 4))
        max_cp = int(gen.get("max_critical_path_rooms", 7))
        min_branch = int(gen.get("min_optional_branch_rooms", 2))
        max_branch = int(gen.get("max_optional_branch_rooms", 4))

        total_rooms = rng.randint(min_rooms, max_rooms)
        cp_rooms = rng.randint(min_cp, min(max_cp, total_rooms))
        branch_rooms = rng.randint(min_branch, min(max_branch, max(2, total_rooms - cp_rooms)))

        rooms = []
        edges = []
        critical_path = []
        optional_branches = []

        # Create critical path rooms: entry ... exit
        for i in range(1, cp_rooms + 1):
            rid = _stable_room_id(i)
            rtype = "entry" if i == 1 else ("exit" if i == cp_rooms else rng.choice(["combat", "resource", "hazard", "false_safety"]))
            pressure_level = self._choose_pressure_level(rng, rtype)
            hazards = self._generate_room_hazards(rng, rtype, difficulty_tier)
            resources = self._generate_room_resources(rng, rtype)
            enemy_influence = _clamp(rng.random() * 0.25 + (0.15 if pressure_level in ("hunted", "critical") else 0.0), 0.0, 1.0)

            rooms.append(
                {
                    "room_id": rid,
                    "room_type": rtype,
                    "pressure_level": pressure_level,
                    "hazards": hazards,
                    "resources": resources,
                    "enemy_influence": float(enemy_influence),
                    "audio_profile": self._choose_room_audio_profile(pressure_level),
                    "visual_profile": "placeholder_readable",
                }
            )
            if self.dressing_manager:
                self.dressing_manager.dress_room(rooms[-1])
            critical_path.append(rid)

            if i > 1:
                edges.append(
                    {
                        "from": _stable_room_id(i - 1),
                        "to": rid,
                        "route_type": "main",
                        "stamina_cost": int(rng.randint(1, 3)),
                        "noise_cost": float(round(rng.uniform(0.0, 0.35), 3)),
                        "hazard_risk": float(round(rng.uniform(0.0, 0.25), 3)),
                    }
                )

        # Optional branch (risk/reward) attached to a non-exit room on the critical path.
        branch_start_index = rng.randint(2, max(2, cp_rooms - 1))
        branch_start = _stable_room_id(branch_start_index)
        branch_ids = []

        # Create branch rooms after critical path ids to keep stable ordering.
        for j in range(1, branch_rooms + 1):
            rid = _stable_room_id(cp_rooms + j)
            rtype = rng.choice(["hazard", "resource", "combat"])
            pressure_level = self._choose_pressure_level(rng, rtype)
            hazards = self._generate_room_hazards(rng, rtype, difficulty_tier)
            resources = self._generate_room_resources(rng, rtype)
            enemy_influence = _clamp(rng.random() * 0.35 + 0.15, 0.0, 1.0)
            rooms.append(
                {
                    "room_id": rid,
                    "room_type": rtype,
                    "pressure_level": pressure_level,
                    "hazards": hazards,
                    "resources": resources,
                    "enemy_influence": float(enemy_influence),
                    "audio_profile": self._choose_room_audio_profile(pressure_level),
                    "visual_profile": "placeholder_readable",
                }
            )
            if self.dressing_manager:
                self.dressing_manager.dress_room(rooms[-1])
            branch_ids.append(rid)

        # Connect branch as resource_branch or risk_branch; dead-end or loopback.
        branch_route_type = rng.choice(["risk_branch", "resource_branch", "ambush"])
        prev = branch_start
        for rid in branch_ids:
            edges.append(
                {
                    "from": prev,
                    "to": rid,
                    "route_type": branch_route_type if prev == branch_start else rng.choice(["dead_end", "risk_branch", "resource_branch"]),
                    "stamina_cost": int(rng.randint(1, 4)),
                    "noise_cost": float(round(rng.uniform(0.1, 0.85), 3)),
                    "hazard_risk": float(round(rng.uniform(0.15, 0.95), 3)),
                }
            )
            prev = rid

        # Optionally loop back to critical path to avoid pure dead-end.
        if rng.random() < 0.55 and len(branch_ids) >= 2:
            loop_to_index = rng.randint(branch_start_index + 1, cp_rooms)
            loop_to = _stable_room_id(loop_to_index)
            edges.append(
                {
                    "from": branch_ids[-1],
                    "to": loop_to,
                    "route_type": "loopback",
                    "stamina_cost": int(rng.randint(1, 4)),
                    "noise_cost": float(round(rng.uniform(0.1, 0.75), 3)),
                    "hazard_risk": float(round(rng.uniform(0.1, 0.75), 3)),
                }
            )

        optional_branches.append({"start": branch_start, "rooms": list(branch_ids), "route_type": branch_route_type})

        floor_id = f"floor_{hashlib.sha256((seed_str + str(difficulty_tier)).encode('utf-8')).hexdigest()[:12]}"
        floor = {
            "floor_id": floor_id,
            "seed": seed_str,
            "difficulty_tier": int(difficulty_tier),
            "rooms": rooms,
            "edges": edges,
            "critical_path": critical_path,
            "optional_branches": optional_branches,
        }

        verdict = self.validate_floor(floor)
        floor["validation"] = verdict
        return floor

    def _adjacency(self, floor: dict):
        adj = {}
        for e in floor.get("edges") or []:
            adj.setdefault(e["from"], []).append(e["to"])
        return adj

    def validate_floor(self, floor: dict):
        rooms = floor.get("rooms") or []
        edges = floor.get("edges") or []
        room_ids = {r.get("room_id") for r in rooms}
        entry = next((r for r in rooms if r.get("room_type") == "entry"), None)
        exit_room = next((r for r in rooms if r.get("room_type") == "exit"), None)

        checks = []

        if entry and exit_room:
            checks.append({"check": "Entry and exit exist", "status": "PASS"})
        else:
            checks.append({"check": "Entry and exit exist", "status": "FAIL"})

        # Edge endpoints must exist
        edge_ok = all((e.get("from") in room_ids and e.get("to") in room_ids) for e in edges)
        checks.append({"check": "Edges reference valid rooms", "status": "PASS" if edge_ok else "FAIL"})

        # Solvable: entry connects to exit
        solvable = False
        if entry and exit_room:
            adj = self._adjacency(floor)
            q = deque([entry["room_id"]])
            seen = {entry["room_id"]}
            while q:
                cur = q.popleft()
                if cur == exit_room["room_id"]:
                    solvable = True
                    break
                for nxt in adj.get(cur, []):
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append(nxt)
        checks.append({"check": "Entry connects to exit", "status": "PASS" if solvable else "FAIL"})

        # At least one safe path: main critical path edges have bounded hazard risk
        safe_edges = [e for e in edges if e.get("route_type") == "main" and float(e.get("hazard_risk", 1.0)) <= 0.35]
        checks.append({"check": "At least one safe path exists", "status": "PASS" if len(safe_edges) >= 1 else "FAIL"})

        # Optional risk/reward branch exists
        branches = floor.get("optional_branches") or []
        checks.append({"check": "At least one optional risk/reward branch exists", "status": "PASS" if len(branches) >= 1 else "FAIL"})

        # Hazards bounded by tier (no instant death)
        tier_cfg = self._hazard_tier_cfg(int(floor.get("difficulty_tier", 1)))
        max_hz = int(tier_cfg.get("max_hazards_per_room", 1))
        bounded_hz = all(len(r.get("hazards") or []) <= max_hz for r in rooms)
        checks.append({"check": "Hazards are bounded by difficulty tier", "status": "PASS" if bounded_hz else "FAIL"})

        verdict = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
        return {"verdict": verdict, "checks": checks}

    def summarize_floor(self, floor: dict, current_room_id: str | None = None):
        rooms = floor.get("rooms") or []
        edges = floor.get("edges") or []
        cur = current_room_id
        cur_room = next((r for r in rooms if r.get("room_id") == cur), None) if cur else None
        return {
            "floor_id": floor.get("floor_id"),
            "seed": floor.get("seed"),
            "difficulty_tier": floor.get("difficulty_tier"),
            "room_count": len(rooms),
            "edge_count": len(edges),
            "current_room": (cur_room or {}).get("room_id"),
            "current_room_type": (cur_room or {}).get("room_type"),
            "current_pressure_level": (cur_room or {}).get("pressure_level"),
            "critical_path_len": len(floor.get("critical_path") or []),
            "branch_count": len(floor.get("optional_branches") or []),
        }

    def evaluate_room_hazards(self, seed: str, room_id: str, hazards: list, difficulty_tier: int):
        """
        Deterministic hazard evaluation for a specific room based on (seed, room_id).
        Returns bounded damage/pressure/noise effects for the room entry.
        """
        if not hazards:
            return {"damage": 0, "pressure_gain": 0, "noise_gain": 0.0, "hazards": []}

        tier_cfg = self._hazard_tier_cfg(int(difficulty_tier))
        max_damage = int(tier_cfg.get("max_room_damage", 15))
        max_pressure = int(tier_cfg.get("max_room_pressure_gain", 12))

        rng = random.Random(int(hashlib.sha256(f"{seed}:{room_id}".encode("utf-8")).hexdigest()[:16], 16))
        effects_cfg = self.hazard_profile.get("hazard_effects") or {}

        total_damage = 0
        total_pressure = 0
        total_noise = 0.0
        applied = []
        for hz in list(hazards):
            cfg = effects_cfg.get(hz) or {}
            dr = cfg.get("damage_range") or [0, 0]
            pr = cfg.get("pressure_gain_range") or [0, 0]
            damage = int(rng.randint(int(dr[0]), int(dr[1]))) if len(dr) == 2 else 0
            pressure = int(rng.randint(int(pr[0]), int(pr[1]))) if len(pr) == 2 else 0
            noise = float(cfg.get("noise_gain", 0.0))
            total_damage += damage
            total_pressure += pressure
            total_noise += noise
            applied.append({"type": hz, "damage": damage, "pressure_gain": pressure, "noise_gain": noise})

        total_damage = int(_clamp(total_damage, 0, max_damage))
        total_pressure = int(_clamp(total_pressure, 0, max_pressure))
        total_noise = float(_clamp(total_noise, 0.0, 1.0))
        return {"damage": total_damage, "pressure_gain": total_pressure, "noise_gain": total_noise, "hazards": applied}

    def apply_world_memory(self, floor: dict, world_memory_snapshot: dict | None):
        """
        Apply subtle, bounded residue metadata onto the generated floor without breaking solvability.
        Does not change topology; only annotates rooms/edges to shape future pressure/audio/enemy signals.
        """
        if not floor or not world_memory_snapshot:
            return floor

        fairness = ((world_memory_snapshot.get("fairness") or {}) if isinstance(world_memory_snapshot.get("fairness"), dict) else {})
        max_enemy_bump = float(fairness.get("max_enemy_influence_bump", 0.2) or 0.2)
        max_pressure_bump = int(fairness.get("max_pressure_bump_from_memory", 6) or 6)

        room_scars = world_memory_snapshot.get("room_scars") or {}
        route_fear = world_memory_snapshot.get("route_fear") or {}
        hazard_reactivation = world_memory_snapshot.get("hazard_reactivation") or {}

        rooms = floor.get("rooms") or []
        for r in rooms:
            rid = r.get("room_id")
            scar = float(room_scars.get(str(rid), 0.0) or 0.0)
            if scar <= 0:
                continue
            r["scar_level"] = float(_clamp(scar, 0.0, 1.0))
            r["visual_decay_marker"] = True
            r["visual_trace_overlay"] = True
            # Increase local enemy influence slightly
            r["enemy_influence"] = float(_clamp(float(r.get("enemy_influence", 0.0)) + (scar * max_enemy_bump), 0.0, 1.0))

            # Subtle pressure bump: store as metadata for runtime to interpret (bounded).
            r["memory_pressure_bump"] = int(_clamp(round(scar * max_pressure_bump), 0, max_pressure_bump))

            # Hazard reactivation: annotate probability (bounded) per room based on past triggers.
            room_hz = []
            for k, v in (hazard_reactivation.items() if isinstance(hazard_reactivation, dict) else []):
                if str(k).startswith(f"{rid}:"):
                    room_hz.append(float(v))
            if room_hz:
                r["hazard_reactivation_chance"] = float(_clamp(max(room_hz), 0.0, 1.0))

        edges = floor.get("edges") or []
        for e in edges:
            k = f"{e.get('from')}->{e.get('to')}"
            fear = float(route_fear.get(k, 0.0) or 0.0)
            if fear > 0:
                e["route_fear"] = float(_clamp(fear, 0.0, 1.0))
        return floor
