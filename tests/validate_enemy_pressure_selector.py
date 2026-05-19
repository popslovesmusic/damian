import os
import json
import sys

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from engine.enemies.runtime import enemy_pressure_selector

def run_enemy_pressure_selector_audit():
    audit_results = {
        "patch_id": "TOWER-ENGINE-047",
        "verdict": "FAIL",
        "checks": []
    }

    # Paths
    selector_path = os.path.join(project_root, "engine/enemies/runtime/enemy_pressure_selector.py")
    
    # Check 1: enemy_pressure_selector.py exists
    exists_check = {"check": "enemy_pressure_selector.py exists", "status": "PASS"}
    if not os.path.exists(selector_path):
        exists_check["status"] = "FAIL"
        exists_check["reason"] = "File not found"
    audit_results["checks"].append(exists_check)

    if exists_check["status"] == "FAIL":
        write_results(audit_results)
        return audit_results

    # Check 2: Required selector functions exist
    required_funcs = ["select_enemy_archetype", "calculate_pressure_bias", "build_enemy_pressure_profile", "summarize_enemy_pressure_profile"]
    funcs_check = {"check": "Required selector functions exist", "status": "PASS"}
    missing_funcs = [func for func in required_funcs if not hasattr(enemy_pressure_selector, func)]
    if missing_funcs:
        funcs_check["status"] = "FAIL"
        funcs_check["reason"] = f"Missing functions: {', '.join(missing_funcs)}"
    audit_results["checks"].append(funcs_check)

    # Setup for functional checks
    fm_low = {
        "floor_id": 1, "mutation_level": 0, "stability": 1.0, "residue_history": []
    }
    fm_potion = {
        "floor_id": 1, "mutation_level": 0, "stability": 1.0, 
        "residue_history": [{"residue_id": "p1", "tags": ["high_potion_usage"]}, {"residue_id": "p2", "tags": ["potion"]}, {"residue_id": "p3", "tags": ["potion"]}]
    }
    fm_strategy = {
        "floor_id": 1, "mutation_level": 0, "stability": 1.0,
        "residue_history": [{"residue_id": "s1", "tags": ["repeated_strategy"]}, {"residue_id": "s2", "tags": ["repeated_strategy"]}]
    }
    fm_instable = {
        "floor_id": 1, "mutation_level": 0, "stability": 0.3, "residue_history": []
    }

    # Check 3: Determinism
    det_check = {"check": "Selection is deterministic", "status": "PASS"}
    if enemy_pressure_selector.select_enemy_archetype(fm_low) != enemy_pressure_selector.select_enemy_archetype(fm_low):
        det_check["status"] = "FAIL"
        det_check["reason"] = "Selection differs for same input"
    audit_results["checks"].append(det_check)

    # Check 4: Bias checks (we check if bias weights reflect logic)
    bias_check = {"check": "Biases reflect residue state", "status": "PASS"}
    b_low = enemy_pressure_selector.calculate_pressure_bias(fm_low)
    b_potion = enemy_pressure_selector.calculate_pressure_bias(fm_potion)
    b_strategy = enemy_pressure_selector.calculate_pressure_bias(fm_strategy)
    b_instable = enemy_pressure_selector.calculate_pressure_bias(fm_instable)
    
    reasons = []
    if b_low.get("pressure_unit", 0) <= b_low.get("ambush_unit", 0):
        reasons.append("Low pressure floor didn't bias pressure_unit")
    if b_potion.get("attrition_unit", 0) <= 0.3:
        reasons.append("High potion usage didn't bias attrition_unit")
    if b_strategy.get("counter_unit", 0) <= 0.3:
        reasons.append("Repeated strategy didn't bias counter_unit")
    if b_instable.get("ambush_unit", 0) <= 0.3:
        reasons.append("High instability didn't bias ambush_unit")
        
    if reasons:
        bias_check["status"] = "FAIL"
        bias_check["reason"] = "; ".join(reasons)
    audit_results["checks"].append(bias_check)

    # Check 5: Profile validity
    profile = enemy_pressure_selector.build_enemy_pressure_profile("pressure_unit", fm_low)
    profile_check = {"check": "Pressure profile is valid and bounded", "status": "PASS"}
    if not (0.0 <= profile["base_pressure_rating"] <= 1.0):
        profile_check["status"] = "FAIL"
        profile_check["reason"] = "base_pressure_rating out of range"
    if any(profile["bounded_rules"].values()):
        profile_check["status"] = "FAIL"
        profile_check["reason"] = "Bounded rules are not all False"
    audit_results["checks"].append(profile_check)

    # Check 6: Summarization
    summary = enemy_pressure_selector.summarize_enemy_pressure_profile(profile)
    summary_check = {"check": "Summarization returns readable string", "status": "PASS"}
    if not summary or "Enemy Archetype" not in summary:
        summary_check["status"] = "FAIL"
        summary_check["reason"] = "Summary is empty or invalid"
    audit_results["checks"].append(summary_check)

    # Check 7: No forbidden code
    forbidden_check = {"check": "No forbidden systems introduced", "status": "PASS"}
    with open(selector_path, 'r') as f:
        content = f.read()
        forbidden = ["pygame", "opengl", "gpu", "multiplayer", "network", "pathfinding", "tiles", "spawning", "ai"]
        # Allow 'ai' if it's part of 'available' or similar common terms, but check context
        found = [f for f in forbidden if f in content.lower()]
        # Filter out 'available' for 'ai'
        if "ai" in found and "available" in content.lower() and " ai " not in content.lower():
             found.remove("ai")
             
        if found:
            forbidden_check["status"] = "FAIL"
            forbidden_check["reason"] = f"Found potentially forbidden terms: {', '.join(found)}"
    audit_results["checks"].append(forbidden_check)

    # Final verdict
    if all(check["status"] == "PASS" for check in audit_results["checks"]):
        audit_results["verdict"] = "PASS"
    else:
        audit_results["verdict"] = "FAIL"

    write_results(audit_results)
    return audit_results

def write_results(audit_results):
    output_dir = os.path.join(project_root, "outputs/audits/")
    os.makedirs(output_dir, exist_ok=True)
    audit_file_path = os.path.join(output_dir, "tower_engine_047_enemy_pressure_selector_audit.json")

    validation_results_dir = os.path.join(project_root, "validation/results/")
    os.makedirs(validation_results_dir, exist_ok=True)
    result_file_path = os.path.join(validation_results_dir, "tower_engine_047_enemy_pressure_selector_result.json")

    with open(audit_file_path, 'w') as f:
        json.dump(audit_results, f, indent=2)

    with open(result_file_path, 'w') as f:
        json.dump({"verdict": audit_results["verdict"]}, f, indent=2)

if __name__ == "__main__":
    audit = run_enemy_pressure_selector_audit()
    print(json.dumps(audit, indent=2))
