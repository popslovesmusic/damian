import os
import json
import jsonschema
import pytest

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "engine/combat/combat_system_registry.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "engine/combat/contracts/combat_session.schema.json")
EXAMPLE_PATH = os.path.join(PROJECT_ROOT, "engine/combat/contracts/example_combat_session.json")

def test_combat_registry_exists():
    assert os.path.exists(REGISTRY_PATH), f"Registry not found at {REGISTRY_PATH}"

def test_combat_registry_content():
    with open(REGISTRY_PATH, 'r') as f:
        registry = json.load(f)
    
    assert "bounded_growth_rules" in registry
    assert "no_permanent_invulnerability" in registry["bounded_growth_rules"]
    assert "no_infinite_damage_scaling" in registry["bounded_growth_rules"]
    
    # Check residue pressure rules
    residue_rules = [r for r in registry["bounded_growth_rules"] if "residue" in r]
    assert len(residue_rules) > 0, "No residue pressure rules found in registry"
    
    assert "combat_pipeline_rules" in registry
    assert "combat_results_must_flow_into_existing_mvp_outcome_pipeline" in registry["combat_pipeline_rules"]

def test_combat_session_schema_exists():
    assert os.path.exists(SCHEMA_PATH), f"Schema not found at {SCHEMA_PATH}"

def test_example_validates_against_schema():
    with open(SCHEMA_PATH, 'r') as f:
        schema = json.load(f)
    with open(EXAMPLE_PATH, 'r') as f:
        example = json.load(f)
    
    jsonschema.validate(instance=example, schema=schema)

def test_example_content_requirements():
    with open(EXAMPLE_PATH, 'r') as f:
        example = json.load(f)
    
    # Example includes resource sink usage
    assert example["resource_usage"]["potions_used"] > 0
    assert example["resource_usage"]["repair_items_used"] > 0
    
    # Example includes residue pressure fields
    assert "residue_pressure" in example
    assert "dominant_build_visibility" in example["residue_pressure"]
    
    # Example forbidden flags are all false
    for flag, value in example["forbidden_flags"].items():
        assert value is False, f"Forbidden flag {flag} should be false in example"

def test_no_combat_runtime_implementation():
    # Check that no .py files (other than tests) exist in engine/combat/
    combat_dir = os.path.join(PROJECT_ROOT, "engine/combat/")
    py_files = [f for f in os.listdir(combat_dir) if f.endswith(".py")]
    assert len(py_files) == 0, f"Found unexpected python files in engine/combat/: {py_files}"

if __name__ == "__main__":
    pytest.main([__file__])
