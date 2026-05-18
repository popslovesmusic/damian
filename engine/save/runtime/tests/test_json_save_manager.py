import pytest
import os
import json
import shutil
from engine.save.runtime import json_save_manager

# Define a temporary directory for tests
TEST_DIR = "test_temp_dir"

@pytest.fixture(autouse=True)
def setup_teardown_test_dir():
    """Ensures a clean test directory for each test."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    yield
    shutil.rmtree(TEST_DIR)

# --- Test load_json ---
def test_load_json_success():
    test_path = os.path.join(TEST_DIR, "valid.json")
    test_data = {"key": "value", "number": 123}
    with open(test_path, 'w') as f:
        json.dump(test_data, f)
    
    result = json_save_manager.load_json(test_path)
    assert result["ok"] is True
    assert result["payload"] == test_data

def test_load_json_file_not_found():
    test_path = os.path.join(TEST_DIR, "non_existent.json")
    result = json_save_manager.load_json(test_path)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"
    assert "File not found" in result["message"]

def test_load_json_invalid_json():
    test_path = os.path.join(TEST_DIR, "invalid.json")
    with open(test_path, 'w') as f:
        f.write("{invalid json}")
    
    result = json_save_manager.load_json(test_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidJson"
    assert "Invalid JSON" in result["message"]

# --- Test save_json ---
def test_save_json_success():
    test_path = os.path.join(TEST_DIR, "save_test.json")
    test_data = {"foo": "bar"}
    result = json_save_manager.save_json(test_path, test_data)
    assert result["ok"] is True
    assert os.path.exists(test_path)
    with open(test_path, 'r') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_data

def test_save_json_create_parent_dirs():
    test_path = os.path.join(TEST_DIR, "new_dir", "deep", "save_test.json")
    test_data = {"data": "nested"}
    result = json_save_manager.save_json(test_path, test_data)
    assert result["ok"] is True
    assert os.path.exists(test_path)
    assert os.path.isdir(os.path.join(TEST_DIR, "new_dir", "deep"))

def test_save_json_serialization_error():
    test_path = os.path.join(TEST_DIR, "non_serializable.json")
    non_serializable_data = {"func": lambda x: x} # Lambda functions are not JSON serializable
    result = json_save_manager.save_json(test_path, non_serializable_data)
    assert result["ok"] is False
    assert result["error_type"] == "SerializationError"
    assert "not JSON serializable" in result["message"]

# --- Test validate_json ---
def test_validate_json_success():
    test_payload = {"name": "Test", "age": 30}
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    result = json_save_manager.validate_json(test_payload, test_schema_path)
    assert result["ok"] is True

def test_validate_json_schema_not_found():
    test_payload = {"name": "Test"}
    non_existent_schema_path = os.path.join(TEST_DIR, "non_existent_schema.json")
    result = json_save_manager.validate_json(test_payload, non_existent_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaNotFound"

def test_validate_json_invalid_payload():
    test_payload = {"name": "Test", "age": "thirty"} # age should be integer
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    result = json_save_manager.validate_json(test_payload, test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    assert "is not of type 'integer'" in result["message"]

def test_validate_json_invalid_schema():
    test_payload = {"name": "Test"}
    test_schema_path = os.path.join(TEST_DIR, "invalid_schema.json")
    with open(test_schema_path, 'w') as f:
        f.write("{invalid schema}")
    
    result = json_save_manager.validate_json(test_payload, test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidSchema"
    assert "Invalid JSON in schema file" in result["message"]

# --- Test load_validated_json ---
def test_load_validated_json_success():
    test_payload = {"name": "Test", "age": 30}
    test_path = os.path.join(TEST_DIR, "valid_to_load_and_validate.json")
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_path, 'w') as f:
        json.dump(test_payload, f)
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)

    result = json_save_manager.load_validated_json(test_path, test_schema_path)
    assert result["ok"] is True
    assert result["payload"] == test_payload

def test_load_validated_json_file_not_found():
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {"type": "object"}
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)

    result = json_save_manager.load_validated_json("non_existent.json", test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "FileNotFound"

def test_load_validated_json_invalid_json_in_file():
    test_path = os.path.join(TEST_DIR, "invalid_json_for_load_validate.json")
    with open(test_path, 'w') as f:
        f.write("{invalid json}")
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {"type": "object"}
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)

    result = json_save_manager.load_validated_json(test_path, test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "InvalidJson"

def test_load_validated_json_invalid_payload_against_schema():
    test_payload = {"name": "Test", "age": "thirty"}
    test_path = os.path.join(TEST_DIR, "invalid_payload_for_load_validate.json")
    with open(test_path, 'w') as f:
        json.dump(test_payload, f)
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    result = json_save_manager.load_validated_json(test_path, test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"

# --- Test save_validated_json ---
def test_save_validated_json_success():
    test_payload = {"name": "Test", "age": 30}
    test_path = os.path.join(TEST_DIR, "valid_to_save_and_validate.json")
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    result = json_save_manager.save_validated_json(test_path, test_payload, test_schema_path)
    assert result["ok"] is True
    assert os.path.exists(test_path)
    with open(test_path, 'r') as f:
        loaded_data = json.load(f)
    assert loaded_data == test_payload

def test_save_validated_json_invalid_payload():
    test_payload = {"name": "Test", "age": "thirty"} # age should be integer
    test_path = os.path.join(TEST_DIR, "invalid_to_save_and_validate.json")
    test_schema_path = os.path.join(TEST_DIR, "schema.json")
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"]
    }
    with open(test_schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    result = json_save_manager.save_validated_json(test_path, test_payload, test_schema_path)
    assert result["ok"] is False
    assert result["error_type"] == "SchemaValidationFailure"
    assert not os.path.exists(test_path) # Should not save invalid data
