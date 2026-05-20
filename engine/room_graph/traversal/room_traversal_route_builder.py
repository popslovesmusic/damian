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

# Paths to schemas
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_ROUTE_SCHEMA_PATH = os.path.join(_PROJECT_ROOT, "engine/room_graph/traversal/contracts/room_traversal_route.schema.json")

PATCH_ID = "TOWER-ENGINE-093"
SYSTEM_NAME = "room_traversal_route_builder"

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

def make_environmental_profile(route_type, from_node, to_node, mutation_level=0, debug=False):
    """
    Creates a deterministic environmental profile based on nodes and route type.
    """
    # Deterministic base from difficulty ratings (TOWER-ENGINE-093)
    difficulty_avg = (from_node.get("difficulty_rating", 0.0) + to_node.get("difficulty_rating", 0.0)) / 2.0
    stability_avg = (from_node.get("stability", 1.0) + to_node.get("stability", 1.0)) / 2.0

    # Default profile
    profile = {
        "darkness": round(max(0.0, min(1.0, difficulty_avg * 0.5)), 2),
        "instability": round(max(0.0, min(1.0, (1.0 - stability_avg) + (mutation_level * 0.05))), 2),
        "enemy_exposure": round(max(0.0, min(1.0, difficulty_avg)), 2),
        "resource_drain": round(max(0.0, min(1.0, difficulty_avg * 0.3)), 2),
        "mutation_scarring": round(max(0.0, min(1.0, (mutation_level * 0.1) + (difficulty_avg * 0.2))), 2)
    }

    # Route type adjustments
    if route_type == "recovery_route":
        profile["enemy_exposure"] *= 0.5
        profile["resource_drain"] *= 0.5
    elif route_type == "pressure_route":
        profile["enemy_exposure"] *= 1.2
        profile["resource_drain"] *= 1.5
    elif route_type == "survivor_mark_route":
        profile["instability"] += 0.1
        profile["mutation_scarring"] += 0.1
    elif route_type == "escape_route":
        profile["enemy_exposure"] *= 0.3
        profile["darkness"] *= 0.7

    # Clamp results
    for key in profile:
        profile[key] = round(max(0.0, min(1.0, float(profile[key]))), 2)

    return profile

def calculate_route_exposure(environmental_profile, debug=False):
    """
    Calculates aggregate route exposure (0.0 to 1.0).
    """
    p = environmental_profile
    # Weighted average (TOWER-ENGINE-093)
    exposure = (
        p.get("enemy_exposure", 0.0) * 0.4 +
        p.get("instability", 0.0) * 0.2 +
        p.get("darkness", 0.0) * 0.15 +
        p.get("resource_drain", 0.0) * 0.15 +
        p.get("mutation_scarring", 0.0) * 0.1
    )
    return round(max(0.0, min(1.0, exposure)), 4)

def calculate_escape_modifier(route_type, environmental_profile, debug=False):
    """
    Calculates escape modifier (-1.0 to 1.0).
    """
    base_bias = 0.0
    if route_type == "recovery_route":
        base_bias = 0.15
    elif route_type == "pressure_route":
        base_bias = -0.10
    elif route_type == "escape_route":
        base_bias = 0.25

    # High instability and darkness make it harder to escape
    penalty = (environmental_profile.get("instability", 0.0) * 0.2) + (environmental_profile.get("darkness", 0.0) * 0.1)
    
    result = base_bias - penalty
    return round(max(-1.0, min(1.0, result)), 4)

def build_room_traversal_route(floor_id, from_node, to_node, route_type='primary_route', mutation_level=0, debug=False):
    """
    Builds a schema-compatible RoomTraversalRoute record.
    """
    valid_types = ["primary_route", "side_route", "recovery_route", "pressure_route", "survivor_mark_route", "escape_route"]
    if route_type not in valid_types:
        return {"ok": False, "error": "InvalidRouteType", "message": f"Route type must be one of {valid_types}"}

    profile = make_environmental_profile(route_type, from_node, to_node, mutation_level, debug)
    exposure = calculate_route_exposure(profile, debug)
    modifier = calculate_escape_modifier(route_type, profile, debug)

    # Route type rules (TOWER-ENGINE-093)
    critical = route_type in ["primary_route", "pressure_route"]
    supports_sm = route_type == "survivor_mark_route" or to_node.get("supports_survivor_mark", False)

    route = {
        "route_id": f"route_{floor_id}_{from_node['node_id']}_to_{to_node['node_id']}_{route_type}",
        "floor_id": int(floor_id),
        "from_node_id": from_node["node_id"],
        "to_node_id": to_node["node_id"],
        "route_type": route_type,
        "environmental_profile": profile,
        "route_exposure": exposure,
        "escape_modifier": modifier,
        "supports_survivor_mark": supports_sm,
        "critical_route": critical,
        "playability_preserved": True,
        "identity_preserved": True,
        "bounded_flags_clean": True
    }

    return {
        "ok": True,
        "route": route,
        "summary": summarize_room_traversal_route(route),
        "error": None
    }

def build_routes_from_room_graph(room_graph, debug=False):
    """
    Generates traversal route records for all connections in a room graph.
    """
    if not room_graph:
        return {"ok": False, "error": "MissingRoomGraph", "message": "Room graph is required."}

    floor_id = room_graph.get("floor_id", 1)
    mutation_level = room_graph.get("mutation_level", 0)
    nodes_map = {n["node_id"]: n for n in room_graph.get("nodes", [])}
    
    routes = []
    
    for from_id, node in nodes_map.items():
        for to_id in node.get("connections", []):
            if to_id not in nodes_map:
                continue
            
            to_node = nodes_map[to_id]
            
            # Infer route type (MVP heuristic)
            route_type = "primary_route"
            if to_node.get("node_type") == "recovery_room":
                route_type = "recovery_route"
            elif to_node.get("node_type") == "pressure_room":
                route_type = "pressure_route"
            elif to_node.get("node_type") == "survivor_mark_room":
                route_type = "survivor_mark_route"
            elif "side" in to_id or "secret" in to_id:
                route_type = "side_route"

            res = build_room_traversal_route(floor_id, node, to_node, route_type, mutation_level, debug)
            if res["ok"]:
                routes.append(res["route"])

    return {
        "ok": True,
        "routes": routes,
        "summary": f"Built {len(routes)} traversal routes from room graph.",
        "error": None
    }

def validate_room_traversal_route(route, schema_path=None, debug=False):
    """Validates a route record against its schema."""
    if not _save_manager_available:
        return {"ok": False, "message": "json_save_manager not available."}
    if schema_path is None:
        schema_path = _ROUTE_SCHEMA_PATH
    return json_save_manager.validate_json(route, schema_path, debug=debug)

def summarize_room_traversal_route(route):
    """Returns a human-readable summary of the route."""
    if not route:
        return "No route."
    
    p = route.get("environmental_profile", {})
    summary = f"Route ({route.get('route_type')}): "
    summary += f"{route.get('from_node_id')} -> {route.get('to_node_id')}. "
    summary += f"Exposure: {route.get('route_exposure'):.2f}, "
    summary += f"Escape Mod: {route.get('escape_modifier'):.2f}, "
    summary += f"Enemy: {p.get('enemy_exposure', 0.0):.2f}"
    return summary
