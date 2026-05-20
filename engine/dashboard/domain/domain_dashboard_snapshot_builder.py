import os
import json
import uuid
import datetime

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Import json_save_manager for validation
try:
    from engine.save.runtime import json_save_manager
    _save_manager_available = True
except ImportError:
    _save_manager_available = False

# Import pressure subsystems
try:
    from engine.inventory.runtime import inventory_capacity_pressure
    from engine.traversal.runtime import traversal_pressure_stub
    from engine.domain.reclamation import tower_reclamation_pressure_stub
    from engine.residue.mutation import mutation_scarring_stub
    from engine.traversal.routes import route_hazard_visibility_stub
    from engine.domain.collapse import foothold_collapse_stub
    from engine.domain.social_exchange import survivor_trace_stub
    from engine.domain.social_exchange import abandoned_foothold_discovery_stub
    _pressure_available = True
except ImportError:
    _pressure_available = False

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_SNAPSHOT_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/dashboard/domain/contracts/domain_dashboard_snapshot.schema.json")

PATCH_ID = "TOWER-ENGINE-138"
SYSTEM_NAME = "domain_dashboard_snapshot_builder"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass
    elif not _debug_logger_available and debug_enabled:
        print(f"DEBUG [{SYSTEM_NAME}]: {message}")

def derive_pressure_summary(session_state, debug=False):
    """
    Derives the pressure summary from the current known session state.
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = tower_state.get("current_floor", 1)
    
    # 1. Capacity Pressure
    cap_p = 0.0
    inventory_state = session_state.get("inventory_state")
    if inventory_state and _pressure_available:
        cap_p = inventory_capacity_pressure.calculate_capacity_pressure(inventory_state, debug=debug) or 0.0

    # 2. Mutation Pressure
    mut_p = 0.0
    mutation_count = 0
    for fm in tower_state.get("floor_memory", []):
        if fm.get("floor_id") == current_floor:
            mutation_count = len(fm.get("active_mutations", []))
            break
    mut_p = min(1.0, mutation_count * 0.2)

    # 3. Combat Pressure (Proxy from durability decay activity)
    comb_p = 0.5 if session_state.get("durability_pressure_observed") else 0.1

    # 4. Repair Burden
    rep_b = 0.0
    loadout = session_state.get("equipment_loadout")
    if loadout:
        rep_b = loadout.get("aggregate_pressure", {}).get("repair_pressure", 0.0)

    # 5. Traversal Pressure & Escape Risk
    trav_p = 0.0
    esc_r = 0.0
    if _pressure_available:
        # Use baseline route exposure 0.2 for summary
        trav_p = traversal_pressure_stub.calculate_traversal_pressure(
            capacity_pressure=cap_p, 
            mutation_pressure=mut_p, 
            combat_exposure=comb_p, 
            repair_burden=rep_b,
            route_exposure=0.2,
            debug=debug
        )
        esc_r = traversal_pressure_stub.calculate_escape_risk(trav_p, route_exposure=0.2, debug=debug)

    return {
        "combat_pressure": float(comb_p),
        "traversal_pressure": float(trav_p),
        "escape_risk": float(esc_r),
        "mutation_pressure": float(mut_p),
        "repair_burden": float(rep_b),
        "capacity_pressure": float(cap_p)
    }

def derive_equipment_summary(session_state, debug=False):
    """
    Counts damaged and zero-durability items.
    """
    damaged = 0
    zero = 0
    loadout = session_state.get("equipment_loadout", {})
    for item in loadout.get("equipped_items", []):
        dur = item.get("durability", {})
        curr = dur.get("current", 1)
        max_dur = dur.get("maximum", 1)
        if curr < max_dur:
            damaged += 1
        if curr == 0:
            zero += 1

    # Count repair materials
    rep_mats = 0
    inventory = session_state.get("inventory_state", {})
    for item in inventory.get("items", []):
        if item.get("item_id") == "repair_material_basic":
            rep_mats += item.get("quantity", 0)

    return {
        "damaged_items": damaged,
        "zero_durability_items": zero,
        "repair_materials_remaining": rep_mats
    }

def derive_resource_summary(session_state, debug=False):
    """
    Derives visible inventory currency and item counts.
    """
    inventory = session_state.get("inventory_state", {})
    
    gold = inventory.get("gold", 0.0)
    potions = 0
    rare = 0
    
    for item in inventory.get("items", []):
        if item.get("item_id") == "ash_potion_small":
            potions += item.get("quantity", 0)
        elif item.get("item_id") == "rare_material":
            rare += item.get("quantity", 0)

    return {
        "gold": float(gold),
        "potions": potions,
        "rare_materials": rare
    }

def derive_route_summary(session_state, debug=False):
    """
    Derives known traversal history. 
    """
    # For MVP, we extract this from last_traversal_event if it exists in session
    # or just use defaults.
    return {
        "routes_traversed": session_state.get("routes_traversed_count", 0),
        "highest_route_exposure": session_state.get("highest_route_exposure_observed", 0.0),
        "escape_failures": session_state.get("escape_failures_count", 0)
    }

def derive_residue_summary(session_state, debug=False):
    """
    Derives known floor memory and residue events.
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    
    mutations = 0
    marks = 0
    events = 0
    
    for fm in tower_state.get("floor_memory", []):
        mutations += len(fm.get("active_mutations", []))
        marks += len(fm.get("unclaimed_easter_eggs", []))
        events += len(fm.get("residue_history", []))

    return {
        "mutations_triggered": mutations,
        "survivor_marks": marks,
        "residue_events_logged": events
    }

def derive_domain_claim_summary(session_state, debug=False):
    """
    Aggregates evidence of localized strategic footholds (TOWER-ENGINE-111).
    """
    # Domain claims are stored in the session_state or tower_state (Stage 014)
    # For now, we check session_state["domain_claims"]
    claims = session_state.get("domain_claims", [])
    
    active = 0
    decaying = 0
    overrun = 0
    
    max_maint = 0.0
    max_vis = 0.0
    max_mut = 0.0
    total_rec = 0.0
    hostility_preserved = True
    
    for claim in claims:
        status = claim.get("status", "ACTIVE")
        if status == "ACTIVE":
            active += 1
        elif status == "DECAYING":
            decaying += 1
        elif status == "OVERRUN":
            overrun += 1
            
        max_maint = max(max_maint, claim.get("maintenance_pressure", 0.0))
        max_vis = max(max_vis, claim.get("visibility_pressure", 0.0))
        max_mut = max(max_mut, claim.get("mutation_threat", 0.0))
        total_rec += claim.get("recovery_value", 0.0)
        
        if not claim.get("tower_hostility_preserved", True):
            hostility_preserved = False

    return {
        "active_claims": active,
        "decaying_claims": decaying,
        "overrun_claims": overrun,
        "highest_maintenance_pressure": float(max_maint),
        "highest_visibility_pressure": float(max_vis),
        "highest_mutation_threat": float(max_mut),
        "total_recovery_value": float(total_rec),
        "tower_hostility_preserved": hostility_preserved
    }

def derive_reclamation_pressure(session_state, debug=False):
    """
    Derives aggregate environmental pushback (TOWER-ENGINE-121).
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = tower_state.get("current_floor", 1)
    claims = session_state.get("domain_claims", [])
    
    if _pressure_available:
        return tower_reclamation_pressure_stub.calculate_reclamation_pressure(current_floor, claims, debug=debug)
    else:
        return {
            "floor_id": current_floor,
            "total_reclamation_pressure": 0.0,
            "visibility_contribution": 0.0,
            "decay_contribution": 0.0,
            "depth_contribution": 0.0,
            "reclamation_band": "STABLE",
            "mutation_risk_bias": 0.0,
            "bounded_flags_clean": True
        }

def derive_mutation_scarring_summary(session_state, debug=False):
    """
    Aggregates localized environmental degradation (TOWER-ENGINE-129).
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = tower_state.get("current_floor", 1)
    claims = session_state.get("domain_claims", [])
    
    # Identify unique nodes with claims
    nodes = set(c.get("claim_node_id") for c in claims if c.get("claim_node_id"))
    
    max_intensity = 0.0
    agg_hazard = 0.0
    
    if _pressure_available:
        for node_id in nodes:
            # We use 0.0 base residue for dashboard derivation unless stored in session
            scar_res = mutation_scarring_stub.calculate_localized_scarring(node_id, claims, current_floor, debug=debug)
            max_intensity = max(max_intensity, scar_res["scar_intensity"])
            agg_hazard += scar_res["hazard_bias"]
            
    return {
        "scarred_nodes_count": len(nodes),
        "highest_scar_intensity": float(max_intensity),
        "aggregate_hazard_bias": float(agg_hazard),
        "bounded_flags_clean": True
    }


def derive_foothold_collapse_summary(session_state, debug=False):
    """
    Aggregates partial foothold collapse evidence (Stage-018 / TOWER-ENGINE-147).

    Collapse is derived from claim instability and status; it is not deletion.
    """
    claims = session_state.get("domain_claims", [])
    if not claims or not _pressure_available:
        return {
            "claims_evaluated": len(claims),
            "collapsed_footholds": 0,
            "highest_collapse_level": 0.0,
            "collapse_bands_observed": [],
            "bounded_flags_clean": True
        }

    collapsed = 0
    highest = 0.0
    bands = set()

    for claim in claims:
        try:
            record = foothold_collapse_stub.evaluate_foothold_collapse(claim, instability_record=None, debug=debug)
            level = float(record.get("collapse_level", 0.0) or 0.0)
            highest = max(highest, level)
            band = record.get("collapse_band")
            if band:
                bands.add(band)
            if level > 0.0:
                collapsed += 1
        except Exception:
            continue

    return {
        "claims_evaluated": len(claims),
        "collapsed_footholds": int(collapsed),
        "highest_collapse_level": float(highest),
        "collapse_bands_observed": sorted(list(bands)),
        "bounded_flags_clean": True
    }


def derive_foothold_recovery_summary(session_state, debug=False):
    """
    Aggregates foothold recovery actions (Stage-019 / TOWER-ENGINE-156).
    """
    history = session_state.get("foothold_recovery_history", []) or []
    actions = [h for h in history if isinstance(h, dict)]

    total_spent = 0.0
    restored_to_active = 0
    restored_from_overrun = 0
    latest = None

    for rec in actions:
        total_spent += float(rec.get("shards_spent", 0.0) or 0.0)
        if rec.get("new_status") == "ACTIVE" and rec.get("previous_status") != "ACTIVE":
            restored_to_active += 1
        if rec.get("previous_status") == "OVERRUN" and rec.get("new_status") != "OVERRUN":
            restored_from_overrun += 1
        latest = rec

    return {
        "recovery_actions_taken": int(len(actions)),
        "total_shards_spent": float(round(total_spent, 4)),
        "restored_to_active": int(restored_to_active),
        "restored_from_overrun": int(restored_from_overrun),
        "latest_recovery": latest,
        "bounded_flags_clean": True
    }


def derive_survivor_trace_summary(session_state, debug=False):
    """
    Aggregates survivor traces derived from floor memory (Stage-020 / TOWER-ENGINE-166).
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = int(tower_state.get("current_floor", 1) or 1)

    fm = None
    for rec in tower_state.get("floor_memory", []) or []:
        if rec.get("floor_id") == current_floor:
            fm = rec
            break

    if not fm or not _pressure_available:
        return {
            "floor_id": current_floor,
            "traces_observed": 0,
            "strongest_reliability": 0.0,
            "reliability_bands_observed": [],
            "bounded_flags_clean": True
        }

    traces_res = survivor_trace_stub.generate_survivor_traces(fm, max_traces=3, debug=debug)
    traces = traces_res.get("payload", {}).get("traces", []) if traces_res.get("ok") else []
    strongest = 0.0
    bands = set()
    for t in traces or []:
        strongest = max(strongest, float(t.get("reliability", 0.0) or 0.0))
        b = t.get("reliability_band")
        if b:
            bands.add(b)

    return {
        "floor_id": current_floor,
        "traces_observed": int(len(traces or [])),
        "strongest_reliability": float(round(strongest, 4)),
        "reliability_bands_observed": sorted(list(bands)),
        "bounded_flags_clean": True
    }


def derive_abandoned_foothold_summary(session_state, debug=False):
    """
    Aggregates abandoned foothold discovery evidence (Stage-020 / TOWER-ENGINE-166).
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = int(tower_state.get("current_floor", 1) or 1)

    fm = None
    for rec in tower_state.get("floor_memory", []) or []:
        if rec.get("floor_id") == current_floor:
            fm = rec
            break

    if not fm or not _pressure_available:
        return {
            "floor_id": current_floor,
            "discoveries_observed": 0,
            "highest_hazard_risk": 0.0,
            "bounded_flags_clean": True
        }

    disc_res = abandoned_foothold_discovery_stub.discover_abandoned_footholds(fm, scan_intensity=1, debug=debug)
    discoveries = disc_res.get("payload", {}).get("discoveries", []) if disc_res.get("ok") else []
    highest_hazard = 0.0
    for d in discoveries or []:
        highest_hazard = max(highest_hazard, float(d.get("hazard_risk", 0.0) or 0.0))

    return {
        "floor_id": current_floor,
        "discoveries_observed": int(len(discoveries or [])),
        "highest_hazard_risk": float(round(highest_hazard, 4)),
        "bounded_flags_clean": True
    }

def derive_route_visibility_summary(session_state, debug=False):
    """
    Aggregates reconnaissance evidence (TOWER-ENGINE-138).
    """
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    current_floor = tower_state.get("current_floor", 1)
    claims = session_state.get("domain_claims", [])
    
    # We need a list of routes to calculate visibility.
    # In a real session, these would come from the floor's room graph.
    # For dashboard derivation, we attempt to build them or use a baseline.
    
    avg_accuracy = 0.0
    best_band = "UNKNOWN"
    recon_level = 0.0
    
    if _pressure_available:
        # Mock/Baseline routes for dashboard summary if graph not available
        # (Ideally this should use session_state.get("last_room_routes"))
        from engine.traversal.routes import manual_route_selection_stub
        route_types = ["stable_primary", "unstable_alpha", "scarred_corridor"]
        
        accuracies = []
        bands = []
        
        for rt in route_types:
            route = {"route_id": f"baseline_{rt}", "route_type": rt}
            vis = route_hazard_visibility_stub.calculate_route_visibility(route, claims, current_floor, debug=debug)
            accuracies.append(vis["information_accuracy"])
            bands.append(vis["visibility_band"])
            
        if accuracies:
            avg_accuracy = sum(accuracies) / len(accuracies)
            recon_level = avg_accuracy # Proxy
            
            # Identify best band
            band_priority = {"DETAILED": 4, "CLEAR": 3, "RECONNOITERED": 2, "VAGUE": 1, "UNKNOWN": 0}
            best_band = max(bands, key=lambda b: band_priority.get(b, 0))
            
    return {
        "average_information_accuracy": float(avg_accuracy),
        "best_visibility_band": best_band,
        "reconnaissance_level": float(recon_level),
        "bounded_flags_clean": True
    }

def derive_recoverability_status(session_state, debug=False):
    """
    Evaluates if the session is recoverable.
    """
    pressure = derive_pressure_summary(session_state, debug=debug)
    reclamation = derive_reclamation_pressure(session_state, debug=debug)
    scarring = derive_mutation_scarring_summary(session_state, debug=debug)
    
    # Simple heuristic for MVP
    critical = (pressure["combat_pressure"] > 0.9 or 
                pressure["capacity_pressure"] > 0.9 or 
                reclamation["total_reclamation_pressure"] > 0.8 or
                scarring["highest_scar_intensity"] > 0.8)
    
    return {
        "recoverable": True, # Always true in MVP
        "critical_pressure": critical
    }

def build_domain_dashboard_snapshot(session_state, debug=False):
    """
    Builds a schema-compatible DomainDashboardSnapshot.
    """
    _log_debug_event("INFO", "SnapshotStart", "Building dashboard snapshot.", debug_enabled=debug)
    
    tower_state = session_state.get("runtime_context", {}).get("tower_state", {})
    player_prog = session_state.get("runtime_context", {}).get("player_progression", {})
    
    snapshot = {
        "snapshot_id": f"snap_{uuid.uuid4()}",
        "player_id": player_prog.get("player_id", "player_default"),
        "floor_id": int(tower_state.get("current_floor", 1)),
        "run_status": "ACTIVE" if session_state.get("session_active") else "RETREATED",
        "pressure_summary": derive_pressure_summary(session_state, debug=debug),
        "equipment_summary": derive_equipment_summary(session_state, debug=debug),
        "resource_summary": derive_resource_summary(session_state, debug=debug),
        "route_summary": derive_route_summary(session_state, debug=debug),
        "residue_summary": derive_residue_summary(session_state, debug=debug),
        "domain_claim_summary": derive_domain_claim_summary(session_state, debug=debug),
        "reclamation_pressure": derive_reclamation_pressure(session_state, debug=debug),
        "mutation_scarring_summary": derive_mutation_scarring_summary(session_state, debug=debug),
        "foothold_collapse_summary": derive_foothold_collapse_summary(session_state, debug=debug),
        "foothold_recovery_summary": derive_foothold_recovery_summary(session_state, debug=debug),
        "survivor_trace_summary": derive_survivor_trace_summary(session_state, debug=debug),
        "abandoned_foothold_summary": derive_abandoned_foothold_summary(session_state, debug=debug),
        "route_visibility_summary": derive_route_visibility_summary(session_state, debug=debug),
        "recoverability_status": derive_recoverability_status(session_state, debug=debug),
        "bounded_flags_clean": True
    }

    _log_debug_event("INFO", "SnapshotComplete", f"Dashboard snapshot created: {snapshot['snapshot_id']}", debug_enabled=debug)

    return {
        "ok": True,
        "snapshot": snapshot,
        "summary": summarize_dashboard_snapshot(snapshot),
        "error": None
    }

def validate_dashboard_snapshot(snapshot, schema_path=None, debug=False):
    """Validates a snapshot record against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _SNAPSHOT_SCHEMA_PATH
    return json_save_manager.validate_json(snapshot, schema_path, debug=debug)

def summarize_dashboard_snapshot(snapshot):
    """Returns a human-readable summary of the dashboard snapshot."""
    if not snapshot:
        return "No snapshot."
    
    p = snapshot.get("pressure_summary", {})
    r = snapshot.get("resource_summary", {})
    e = snapshot.get("equipment_summary", {})
    dc = snapshot.get("domain_claim_summary", {})
    rec = snapshot.get("reclamation_pressure", {})
    scar = snapshot.get("mutation_scarring_summary", {})
    col = snapshot.get("foothold_collapse_summary", {})
    recov = snapshot.get("foothold_recovery_summary", {})
    traces = snapshot.get("survivor_trace_summary", {})
    abandoned = snapshot.get("abandoned_foothold_summary", {})
    vis = snapshot.get("route_visibility_summary", {})
    
    summary = f"Dashboard Snapshot [{snapshot.get('snapshot_id')[:8]}]: Floor {snapshot.get('floor_id')}. "
    summary += f"Pressure (Combat:{p.get('combat_pressure'):.2f}, Cap:{p.get('capacity_pressure'):.2f}). "
    summary += f"Reclamation: {rec.get('reclamation_band')} ({rec.get('total_reclamation_pressure'):.2f}). "
    summary += f"Scarring: {scar.get('highest_scar_intensity'):.2f} ({scar.get('scarred_nodes_count')} nodes). "
    summary += f"Collapse: {col.get('highest_collapse_level', 0.0):.2f} ({col.get('collapsed_footholds', 0)} footholds). "
    summary += f"Recovery: {recov.get('recovery_actions_taken', 0)} actions ({recov.get('total_shards_spent', 0.0)} shards). "
    summary += f"Traces: {traces.get('traces_observed', 0)} ({traces.get('strongest_reliability', 0.0):.2f}). "
    summary += f"Abandoned: {abandoned.get('discoveries_observed', 0)} ({abandoned.get('highest_hazard_risk', 0.0):.2f}). "
    summary += f"Recon: {vis.get('best_visibility_band')} ({vis.get('average_information_accuracy'):.2f}). "
    summary += f"Resources (Gold:{r.get('gold')}, Potions:{r.get('potions')}). "
    summary += f"Gear ({e.get('damaged_items')} damaged). "
    summary += f"Claims ({dc.get('active_claims')} active"
    if dc.get("decaying_claims", 0) > 0:
        summary += f", {dc.get('decaying_claims')} decaying"
    if dc.get("overrun_claims", 0) > 0:
        summary += f", {dc.get('overrun_claims')} overrun"
    summary += ")."
    return summary
