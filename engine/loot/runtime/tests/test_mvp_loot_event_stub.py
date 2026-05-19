import pytest
import os
import json
from engine.loot.runtime import mvp_loot_event_stub

def test_make_combat_loot_event_victory():
    """Validates loot for VICTORY_ASCEND."""
    result = mvp_loot_event_stub.make_combat_loot_event(1, outcome='VICTORY_ASCEND')
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["rewards"]["gold"] == 10000
    assert payload["rewards"]["stability_shards"] == 1
    assert payload["source"] == 'combat_reward'
    assert payload["bounded_reward_flags"]["grants_invulnerability"] is False

def test_make_combat_loot_event_defeat():
    """Validates loot for DEFEAT_DROP."""
    result = mvp_loot_event_stub.make_combat_loot_event(1, outcome='DEFEAT_DROP')
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["rewards"]["gold"] == 1500
    assert payload["rewards"]["stability_shards"] == 0
    assert payload["rewards"]["residue_fragments"] == 1

def test_make_combat_loot_event_retreat():
    """Validates loot for RETREAT_TO_HUB."""
    result = mvp_loot_event_stub.make_combat_loot_event(1, outcome='RETREAT_TO_HUB')
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["rewards"]["gold"] == 500
    assert payload["rewards"]["stability_shards"] == 0
    assert payload["rewards"]["residue_fragments"] == 0

def test_make_survivor_mark_loot_event():
    """Validates loot for survivor mark reward."""
    result = mvp_loot_event_stub.make_survivor_mark_loot_event(1, "mark_001")
    assert result["ok"] is True
    payload = result["payload"]
    assert payload["rewards"]["gold"] == 2500
    assert payload["rewards"]["stability_shards"] == 2
    assert payload["rewards"]["rare_materials"] == 1
    assert payload["source"] == 'survivor_mark_reward'
    assert payload["survivor_mark_id"] == "mark_001"

def test_loot_event_resource_sink_pressure():
    """Validates resource sink pressure is reported."""
    result = mvp_loot_event_stub.make_combat_loot_event(1)
    payload = result["payload"]
    pressure = payload["resource_sink_pressure"]
    assert pressure["estimated_potion_cost"] == 250
    assert pressure["estimated_repair_cost"] == 120
    assert pressure["estimated_mutation_control_cost"] == 900
    assert pressure["estimated_domain_upkeep_cost"] == 1200

def test_invalid_floor_id():
    """Validates safe failure for invalid floor_id."""
    result = mvp_loot_event_stub.make_combat_loot_event(0)
    assert result["ok"] is False
    assert result["error"] == "InvalidFloorId"
    
    result = mvp_loot_event_stub.make_combat_loot_event(-1)
    assert result["ok"] is False
    
    result = mvp_loot_event_stub.make_combat_loot_event("1")
    assert result["ok"] is False

def test_validate_loot_event_schema():
    """Validates loot event against its schema."""
    result = mvp_loot_event_stub.make_combat_loot_event(1)
    loot_event = result["payload"]
    
    validation = mvp_loot_event_stub.validate_loot_event(loot_event)
    assert validation["ok"] is True

def test_summarize_loot_event():
    """Validates human-readable summary."""
    result = mvp_loot_event_stub.make_combat_loot_event(1)
    loot_event = result["payload"]
    summary = mvp_loot_event_stub.summarize_loot_event(loot_event)
    assert "Gold: 10000" in summary
    assert "Shards: 1" in summary
    assert "combat_reward" in summary
