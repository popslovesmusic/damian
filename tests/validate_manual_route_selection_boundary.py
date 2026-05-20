import json
import jsonschema
import os

SCHEMA_PATH = "engine/traversal/routes/contracts/manual_route_selection.schema.json"
EXAMPLE_PATH = "engine/traversal/routes/contracts/example_manual_route_selection.json"
BOUNDARY_PATH = "engine/traversal/routes/manual_route_selection_boundary.json"

def test_manual_route_selection_boundary():
    # Validate boundary
    with open(BOUNDARY_PATH, 'r') as f:
        boundary = json.load(f)
    assert "route_selection_must_preserve_operational_uncertainty" in boundary["strict_rules"]
    assert "manual_route_selection_must_increase_spatial_agency_without_removing_fear" in boundary["strict_rules"]

    # Validate schema
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)
        
    with open(EXAMPLE_PATH, 'r') as f:
        example = json.load(f)

    jsonschema.validate(instance=example, schema=schema)

if __name__ == "__main__":
    test_manual_route_selection_boundary()
    print("Manual Route Selection Boundary tests passed.")