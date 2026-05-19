import os
import json
import hashlib

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-047"
SYSTEM_NAME = "enemy_pressure_selector"

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

def calculate_pressure_bias(floor_memory, debug=False):
    """
    Calculates bias weights for enemy archetypes based on floor state and residue.
    Returns a dictionary of archetype_id -> bias_weight (0.0 to 1.0).
    """
    if not floor_memory:
        return {}

    biases = {
        "pressure_unit": 0.2,
        "ambush_unit": 0.2,
        "attrition_unit": 0.2,
        "counter_unit": 0.2
    }

    mutation_level = floor_memory.get("mutation_level", 0)
    stability = floor_memory.get("stability", 1.0)
    residue_history = floor_memory.get("residue_history", [])
    
    # 1. Low mutation and low residue pressure biases pressure_unit
    if mutation_level <= 1 and len(residue_history) <= 2:
        biases["pressure_unit"] += 0.4
        _log_debug_event("INFO", "BiasApplied", "Low mutation/residue biasing pressure_unit", debug_enabled=debug)

    # 2. High potion usage biases attrition_unit
    # Check residue history for 'potion' related tags
    potion_residue_count = sum(1 for r in residue_history if "potion" in str(r.get("tags", [])).lower())
    if potion_residue_count >= 3:
        biases["attrition_unit"] += 0.5
        _log_debug_event("INFO", "BiasApplied", "High potion usage biasing attrition_unit", debug_enabled=debug)

    # 3. High repeated strategy pressure biases counter_unit
    strategy_residue_count = sum(1 for r in residue_history if "repeated_strategy" in r.get("tags", []))
    if strategy_residue_count >= 2:
        biases["counter_unit"] += 0.5
        _log_debug_event("INFO", "BiasApplied", "Repeated strategy biasing counter_unit", debug_enabled=debug)

    # 4. High route instability biases ambush_unit
    if stability < 0.6:
        biases["ambush_unit"] += 0.4
        _log_debug_event("INFO", "BiasApplied", "Low stability biasing ambush_unit", debug_enabled=debug)

    # Normalize roughly or just keep as weights
    return biases

def select_enemy_archetype(floor_memory, player_progression=None, debug=False):
    """
    Deterministically selects an enemy archetype based on floor state and biases.
    """
    if not floor_memory:
        return None

    _log_debug_event("INFO", "SelectingArchetype", f"Selecting enemy archetype for floor {floor_memory.get('floor_id')}", debug_enabled=debug)

    biases = calculate_pressure_bias(floor_memory, debug=debug)
    
    # Determinism: sort items and use floor_id + metadata as seed
    archetypes = sorted(biases.items())
    
    # Build a deterministic string to hash
    seed_str = f"floor_{floor_memory.get('floor_id')}_mut_{floor_memory.get('mutation_level')}_stab_{floor_memory.get('stability')}"
    # Add residue IDs for more specific selection
    residue_ids = "".join(sorted([r.get("residue_id", "") for r in floor_memory.get("residue_history", [])]))
    seed_str += f"_res_{residue_ids}"
    
    hash_val = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    
    # Weighted selection (simplistic)
    total_weight = sum(b for a, b in archetypes)
    if total_weight == 0:
        return "pressure_unit" # Default fallback
        
    pick = (hash_val % 1000) / 1000.0 * total_weight
    
    current = 0
    for arch_id, weight in archetypes:
        current += weight
        if pick <= current:
            _log_debug_event("DEBUG", "ArchetypeSelected", f"Selected {arch_id}", {"archetype": arch_id}, debug_enabled=debug)
            return arch_id
            
    return archetypes[-1][0]

def build_enemy_pressure_profile(enemy_archetype_id, floor_memory, debug=False):
    """
    Creates a detailed enemy pressure profile record.
    """
    mutation_level = floor_memory.get("mutation_level", 0) if floor_memory else 0
    stability = floor_memory.get("stability", 1.0) if floor_memory else 1.0
    
    # Base rating influenced by mutation level
    base_rating = 0.2 + (mutation_level * 0.1)
    base_rating = min(0.95, base_rating)
    
    # Calculate biases for reasoning
    biases = calculate_pressure_bias(floor_memory, debug=debug) if floor_memory else {}
    
    reasoning = []
    if floor_memory:
        if mutation_level > 2:
            reasoning.append(f"High mutation level ({mutation_level}) increasing baseline pressure.")
        if stability < 0.7:
            reasoning.append(f"Low floor stability ({stability:.2f}) manifesting ambush opportunities.")
        
        # Add specific adaptation reasoning
        if enemy_archetype_id == "attrition_unit" and biases.get("attrition_unit", 0) > 0.3:
            reasoning.append("Tower adapting to high player resource dependency.")
        if enemy_archetype_id == "counter_unit" and biases.get("counter_unit", 0) > 0.3:
            reasoning.append("Tower manifesting counter-measures against repeated player strategies.")
    
    if not reasoning:
        reasoning.append("Standard tower defense archetype selected.")

    profile = {
        "enemy_archetype_id": enemy_archetype_id,
        "base_pressure_rating": float(base_rating),
        "mutation_level": mutation_level,
        "residue_pressure_bias": float(biases.get("counter_unit", 0.0)),
        "resource_pressure_bias": float(biases.get("attrition_unit", 0.0)),
        "adaptation_reasoning": reasoning,
        "bounded_rules": {
            "unavoidable_defeat": False,
            "requires_god_mode": False,
            "bypasses_pipeline": False
        }
    }
    
    return profile

def summarize_enemy_pressure_profile(profile):
    """
    Returns a human-readable summary of the enemy pressure profile.
    """
    if not profile:
        return "No pressure profile available."
        
    arch = profile.get("enemy_archetype_id", "Unknown")
    rating = profile.get("base_pressure_rating", 0.0)
    reasoning = "\n- ".join(profile.get("adaptation_reasoning", []))
    
    summary = f"Enemy Archetype: {arch} (Pressure: {rating:.2f})\nReasoning:\n- {reasoning}"
    return summary
