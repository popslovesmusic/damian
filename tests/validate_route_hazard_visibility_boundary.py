import json
import jsonschema
import os

SCHEMA_PATH = "engine/traversal/routes/contracts/route_visibility_snapshot.schema.json"
EXAMPLE_PATH = "engine/traversal/routes/contracts/example_route_visibility_snapshot.json"
BOUNDARY_PATH = "engine/traversal/routes/route_hazard_visibility_boundary.json"

def test_route_hazard_visibility_boundary():
    # Validate boundary
    with open(BOUNDARY_PATH, 'r') as f:
        boundary = json.load(f)
    assert "route_visibility_must_be_partial_not_perfect_information" in boundary["strict_rules"]
    assert "route_selection_must_preserve_operational_uncertainty" in boundary["strict_rules"]

    # Validate schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)
        
    with open(EXAMPLE_PATH, 'r') as f:
        example = json.load(f)

    jsonschema.validate(instance=example, schema=schema)
    
    # Assert 'perfect' is not a visibility level
    assert "perfect" not in schema["properties"]["visibility_level"]["enum"]

if __name__ == "__main__":
    test_route_hazard_visibility_boundary()
    print("Route Hazard Visibility Boundary tests passed.")