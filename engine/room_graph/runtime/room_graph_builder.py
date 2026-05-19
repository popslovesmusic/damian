import os
import json
import jsonschema

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-042"
SYSTEM_NAME = "room_graph_builder"

def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    """Helper to log debug events if debug_logger is available and enabled."""
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            # Debug logging failure must not fail the builder
            pass
    elif not _debug_logger_available and debug_enabled:
        print(f"DEBUG [{SYSTEM_NAME}]: {message}")

def _create_structured_error(error_type, message, context=None, debug=False):
    """Creates a structured error dictionary."""
    if debug:
        _log_debug_event("ERROR", error_type, message, context, debug)
    return {"ok": False, "error_type": error_type, "message": message, "context": context or {}}

def _create_structured_success(payload, context=None, debug=False):
    """Creates a structured success dictionary."""
    if debug:
        _log_debug_event("INFO", "OperationSuccess", "Operation completed successfully.", context, debug)
    return {"ok": True, "payload": payload, "context": context or {}}

def make_room_node(node_id, node_type, connections=None, mutation_tags=None, difficulty_rating=0.0, stability=1.0, supports_survivor_mark=False):
    """
    Creates a room node record conforming to room_node.schema.json.
    """
    return {
        "node_id": node_id,
        "node_type": node_type,
        "connections": connections or [],
        "mutation_tags": mutation_tags or [],
        "difficulty_rating": float(difficulty_rating),
        "stability": float(stability),
        "supports_survivor_mark": bool(supports_survivor_mark)
    }

def build_room_graph(floor_record, domain_archetype='tower_domain', include_survivor_mark_room=False, debug=False):
    """
    Builds a deterministic connected room graph record from floor metadata.
    Returns structured success with room_graph or structured error.
    """
    if not floor_record:
        return _create_structured_error("MissingFloorRecord", "Floor record is required.", debug=debug)
    
    floor_id = floor_record.get("floor_id")
    if floor_id is None:
        return _create_structured_error("InvalidFloorId", "Floor record must contain 'floor_id'.", debug=debug)

    if domain_archetype != 'tower_domain':
        # Currently only tower_domain is supported for this skeleton
        return _create_structured_error("UnsupportedDomainArchetype", f"Domain archetype '{domain_archetype}' is not supported.", {"archetype": domain_archetype}, debug=debug)

    _log_debug_event("INFO", "BuildingGraph", f"Building room graph for floor {floor_id}", {"floor_id": floor_id}, debug)

    # Deterministic generation based on floor_id
    # In a real implementation, this would use a seeded RNG or more complex logic.
    # For TOWER-ENGINE-042, we use a fixed MVP shape as per requirements.
    
    nodes = []
    nodes.append(make_room_node("entry_a", "entry_room", connections=["combat_a"], difficulty_rating=0.1, stability=1.0))
    nodes.append(make_room_node("combat_a", "combat_room", connections=["pressure_a", "recovery_a"], difficulty_rating=0.4, stability=0.8))
    nodes.append(make_room_node("pressure_a", "pressure_room", connections=[], difficulty_rating=0.7, stability=0.6))
    nodes.append(make_room_node("recovery_a", "recovery_room", connections=[], difficulty_rating=0.2, stability=0.9))
    
    exit_node_id = "exit_a"
    survivor_mark_nodes = []
    
    if include_survivor_mark_room:
        nodes.append(make_room_node("survivor_mark_a", "survivor_mark_room", connections=[exit_node_id], difficulty_rating=0.3, stability=0.75, supports_survivor_mark=True))
        # Connect pressure and recovery to survivor mark room
        for node in nodes:
            if node["node_id"] in ["pressure_a", "recovery_a"]:
                node["connections"].append("survivor_mark_a")
        survivor_mark_nodes.append("survivor_mark_a")
    else:
        # Connect pressure and recovery directly to exit
        for node in nodes:
            if node["node_id"] in ["pressure_a", "recovery_a"]:
                node["connections"].append(exit_node_id)

    nodes.append(make_room_node(exit_node_id, "exit_room", connections=[], difficulty_rating=0.0, stability=1.0))

    room_graph = {
        "graph_id": f"{domain_archetype}_floor_{floor_id}_graph",
        "floor_id": floor_id,
        "domain_archetype": domain_archetype,
        "layout_seed": f"seed_{floor_id}",
        "nodes": nodes,
        "entry_node_id": "entry_a",
        "exit_node_id": exit_node_id,
        "mutation_level": 0,
        "identity_preserved": True,
        "playability_preserved": True,
        "survivor_mark_nodes": survivor_mark_nodes
    }

    _log_debug_event("DEBUG", "GraphBuilt", "Room graph record constructed.", {"graph_id": room_graph["graph_id"]}, debug)
    
    return _create_structured_success(room_graph, debug=debug)

def validate_room_graph(room_graph, graph_schema_path=None, node_schema_path=None, debug=False):
    """
    Validates a room graph record against schemas.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    
    if not graph_schema_path:
        graph_schema_path = os.path.join(project_root, "engine/room_graph/contracts/room_graph.schema.json")
    
    if not os.path.exists(graph_schema_path):
        return _create_structured_error("SchemaNotFound", f"Graph schema not found at {graph_schema_path}", debug=debug)

    try:
        with open(graph_schema_path, 'r') as f:
            schema = json.load(f)
        
        # Resolver for $ref: "room_node.schema.json"
        base_uri = f"file://{os.path.dirname(graph_schema_path).replace(os.sep, '/')}/"
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        
        jsonschema.validate(instance=room_graph, schema=schema, resolver=resolver)
        return _create_structured_success(True, debug=debug)
    except jsonschema.ValidationError as e:
        return _create_structured_error("SchemaValidationFailure", f"Room graph failed schema validation: {e.message}", debug=debug)
    except Exception as e:
        return _create_structured_error("ValidationError", f"An unexpected error occurred during validation: {e}", debug=debug)

def summarize_room_graph(room_graph):
    """
    Returns a human-readable summary of the room graph.
    """
    if not room_graph:
        return "No room graph provided."
    
    node_count = len(room_graph.get("nodes", []))
    survivor_mark_count = len(room_graph.get("survivor_mark_nodes", []))
    
    return f"Room Graph [{room_graph.get('graph_id')}]: {node_count} nodes, {survivor_mark_count} survivor marks. Entry: {room_graph.get('entry_node_id')}, Exit: {room_graph.get('exit_node_id')}."
