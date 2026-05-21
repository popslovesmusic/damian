import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _stable_pick(items: Sequence[Any], key: str) -> Optional[Any]:
    if not items:
        return None
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(items)
    return items[idx]


def _safe_mkdirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _tower_data_resolve(tower_data_root: str, logical_path: str) -> str:
    p = logical_path.replace("\\", "/")
    if p.startswith("TOWER_DATA/"):
        p = p[len("TOWER_DATA/"):]
    return os.path.normpath(os.path.join(tower_data_root, p))


@dataclass(frozen=True)
class AudioAsset:
    asset_id: str
    source_path: str
    normalized_path: str
    category: str
    duration_seconds: float
    sample_rate_hz: int
    channels: int
    source_format: str
    normalized_format: str
    loudness_target_lufs: float
    peak_db: float
    hash_sha256: str
    duplicate_of: Optional[str]
    license_status: str
    tower_use: str
    notes: str


class AudioAssetLibrary:
    def __init__(self, manifest_path: str, index_path: str, tower_data_root: str):
        self.manifest_path = manifest_path
        self.index_path = index_path
        self.tower_data_root = tower_data_root

        manifest = _load_json(manifest_path)
        self._assets_all: List[AudioAsset] = []
        for raw in manifest.get("assets", []):
            self._assets_all.append(
                AudioAsset(
                    asset_id=str(raw.get("asset_id", "")),
                    source_path=str(raw.get("source_path", "")),
                    normalized_path=str(raw.get("normalized_path", "")),
                    category=str(raw.get("category", "uncategorized")),
                    duration_seconds=float(raw.get("duration_seconds", 0.0) or 0.0),
                    sample_rate_hz=int(raw.get("sample_rate_hz", 0) or 0),
                    channels=int(raw.get("channels", 0) or 0),
                    source_format=str(raw.get("source_format", "")),
                    normalized_format=str(raw.get("normalized_format", "")),
                    loudness_target_lufs=float(raw.get("loudness_target_lufs", 0.0) or 0.0),
                    peak_db=float(raw.get("peak_db", 0.0) or 0.0),
                    hash_sha256=str(raw.get("hash_sha256", "")),
                    duplicate_of=raw.get("duplicate_of"),
                    license_status=str(raw.get("license_status", "unknown")),
                    tower_use=str(raw.get("tower_use", "exclude")),
                    notes=str(raw.get("notes", "")),
                )
            )

        self._index_by_category: Dict[str, List[str]] = _load_json(index_path)
        self._by_id: Dict[str, AudioAsset] = {a.asset_id: a for a in self._assets_all}

    def required_categories(self) -> List[str]:
        return [
            "ambience",
            "pressure",
            "movement",
            "interaction",
            "combat",
            "metal_structure",
            "steam_machine",
            "ui",
            "cathedral",
            "music_texture",
        ]

    def assets_for_category(self, category: str, include_duplicates: bool = False) -> List[AudioAsset]:
        ids = self._index_by_category.get(category, [])
        out: List[AudioAsset] = []
        for asset_id in ids:
            a = self._by_id.get(asset_id)
            if not a:
                continue
            if (not include_duplicates) and a.duplicate_of:
                continue
            out.append(a)
        return out

    def resolve_asset_path(self, asset: AudioAsset) -> str:
        return _tower_data_resolve(self.tower_data_root, asset.normalized_path)


class AudioPressureManager:
    """STAGE-069 runtime layering: generate a deterministic audio plan from normalized assets."""

    def __init__(
        self,
        tower_data_root: str,
        runtime_contract_path: str,
        mix_profiles_path: str,
        event_map_path: str,
    ):
        self.tower_data_root = tower_data_root
        self.contract = _load_json(runtime_contract_path)
        self.mix_profiles = _load_json(mix_profiles_path)
        self.event_map = _load_json(event_map_path)

        audio_root = _tower_data_resolve(tower_data_root, self.contract["audio_root"])
        manifest_path = os.path.join(audio_root, self.contract["library"]["manifest_relpath"])
        index_path = os.path.join(audio_root, self.contract["library"]["index_relpath"])
        self.library = AudioAssetLibrary(manifest_path, index_path, tower_data_root)

    def _pressure_state(self, game_state: Dict[str, Any]) -> str:
        explicit = game_state.get("pressure_state")
        if explicit in self.mix_profiles.get("pressure_states", {}):
            return str(explicit)

        pressure = float(game_state.get("pressure", 0) or 0)
        if pressure >= 80:
            return "critical"
        if pressure >= 60:
            return "hunted"
        if pressure >= 30:
            return "uneasy"
        return "calm"

    def _biome_key(self, game_state: Dict[str, Any]) -> str:
        return str(game_state.get("biome") or game_state.get("location") or "tower").lower()

    def _select_loop(self, category: str, key: str) -> Tuple[Optional[AudioAsset], List[str]]:
        warnings: List[str] = []
        pool = self.library.assets_for_category(category)
        if not pool:
            warnings.append(f"missing_category:{category}")
            return None, warnings
        chosen = _stable_pick(pool, key)
        if not chosen:
            warnings.append(f"no_pick:{category}")
            return None, warnings
        resolved = self.library.resolve_asset_path(chosen)
        if not os.path.exists(resolved):
            warnings.append(f"missing_file:{chosen.normalized_path}")
            return None, warnings
        return chosen, warnings

    def _select_event_sfx(self, category: str, event_key: str) -> Tuple[Optional[AudioAsset], List[str]]:
        warnings: List[str] = []
        pool = [a for a in self.library.assets_for_category(category) if a.duration_seconds <= 20.0]
        if not pool:
            pool = self.library.assets_for_category(category)
        if not pool:
            warnings.append(f"missing_category:{category}")
            return None, warnings
        chosen = _stable_pick(pool, event_key)
        resolved = self.library.resolve_asset_path(chosen)
        if not os.path.exists(resolved):
            warnings.append(f"missing_file:{chosen.normalized_path}")
            return None, warnings
        return chosen, warnings

    def _asset_ref(self, asset: Optional[AudioAsset]) -> Dict[str, Any]:
        if not asset:
            return {}
        return {
            "asset_id": asset.asset_id,
            "category": asset.category,
            "normalized_path": asset.normalized_path,
            "resolved_path": self.library.resolve_asset_path(asset),
            "duration_seconds": asset.duration_seconds,
            "channels": asset.channels,
            "sample_rate_hz": asset.sample_rate_hz,
            "license_status": asset.license_status,
        }

    def plan_audio_state(
        self,
        game_state: Dict[str, Any],
        events: Optional[List[Dict[str, Any]]] = None,
        audit_output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        events = events or []
        pressure_state = self._pressure_state(game_state)
        biome_key = self._biome_key(game_state)

        profile = self.mix_profiles["pressure_states"][pressure_state]
        warnings: List[str] = []

        mix: Dict[str, Any] = {}

        base_amb, w = self._select_loop("ambience", f"base_ambience|{pressure_state}|{biome_key}")
        warnings.extend(w)
        mix["base_ambience"] = {
            "volume": float(profile.get("ambience_volume", 0.65)),
            "assets": ([self._asset_ref(base_amb)] if base_amb else []),
        }

        pressure_loop, w = self._select_loop("pressure", f"pressure|{pressure_state}|{biome_key}")
        warnings.extend(w)
        pressure_vol = float(profile.get("pressure_volume", 0.0))
        mix["pressure"] = {
            "volume": pressure_vol,
            "assets": ([self._asset_ref(pressure_loop)] if (pressure_loop and pressure_vol > 0) else []),
            "stinger_chance": float(profile.get("stinger_chance", 0.0)),
        }

        metal, w = self._select_loop("metal_structure", f"structure_metal|{pressure_state}|{biome_key}")
        warnings.extend(w)
        steam, w = self._select_loop("steam_machine", f"structure_steam|{pressure_state}|{biome_key}")
        warnings.extend(w)
        mix["structure"] = {
            "volume": float(self.mix_profiles.get("layer_defaults", {}).get("structure_volume", 0.25)),
            "assets": [self._asset_ref(a) for a in [metal, steam] if a],
        }

        mix["silence"] = {
            "enabled": bool(profile.get("silence_pulse_enabled", False)),
            "pulse": self.mix_profiles.get("silence_pulse", {}),
        }

        movement_assets: List[Dict[str, Any]] = []
        interaction_assets: List[Dict[str, Any]] = []
        combat_assets: List[Dict[str, Any]] = []
        ui_assets: List[Dict[str, Any]] = []

        for e in events:
            etype = str(e.get("type", "")).upper()
            ek = str(e.get("id", etype))
            mapping = self.event_map.get("events", {}).get(etype)
            if not mapping:
                continue

            category = str(mapping.get("category", "uncategorized"))
            layer = str(mapping.get("layer", ""))
            chosen, w = self._select_event_sfx(category, f"event|{etype}|{ek}|{pressure_state}|{biome_key}")
            warnings.extend(w)
            if not chosen:
                continue

            ref = self._asset_ref(chosen)
            if layer == "movement":
                movement_assets.append(ref)
            elif layer == "interaction":
                interaction_assets.append(ref)
            elif layer == "combat":
                combat_assets.append(ref)
            elif layer == "ui":
                ui_assets.append(ref)

        mix["movement"] = {
            "volume": float(self.mix_profiles.get("layer_defaults", {}).get("movement_volume", 0.9)),
            "assets": movement_assets,
        }
        mix["interaction"] = {
            "volume": float(self.mix_profiles.get("layer_defaults", {}).get("interaction_volume", 0.9)),
            "assets": interaction_assets,
        }
        mix["combat"] = {
            "volume": float(self.mix_profiles.get("layer_defaults", {}).get("combat_volume", 1.0)),
            "assets": combat_assets,
        }
        mix["ui"] = {
            "volume": float(self.mix_profiles.get("layer_defaults", {}).get("ui_volume", 0.8)),
            "assets": ui_assets,
        }

        result = {"pressure_state": pressure_state, "mix": mix, "warnings": sorted(set(warnings))}

        if audit_output_path:
            self.write_audit(audit_output_path, {"game_state": game_state, "events": events, "result": result})

        return result

    def write_audit(self, audit_output_path: str, payload: Dict[str, Any]) -> None:
        out_path = os.path.normpath(audit_output_path)
        _safe_mkdirs(os.path.dirname(out_path))
        doc = {
            "stage": "STAGE-069",
            "patch_id": "STAGE-069-AUDIO-RUNTIME-LAYERING-002",
            "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "audio_root": self.contract.get("audio_root"),
            "payload": payload,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)

    def validate_library(self) -> Dict[str, Any]:
        warnings: List[str] = []
        for cat in self.library.required_categories():
            assets = self.library.assets_for_category(cat)
            if not assets:
                warnings.append(f"missing_category:{cat}")

        return {
            "manifest_path": self.library.manifest_path,
            "index_path": self.library.index_path,
            "warnings": warnings,
        }

