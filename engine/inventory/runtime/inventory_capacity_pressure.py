import os
import json

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

PATCH_ID = "TOWER-ENGINE-070"
SYSTEM_NAME = "inventory_capacity_pressure"

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

def calculate_capacity_pressure(inventory_state, debug=False):
    """
    Calculates capacity_pressure = used_capacity / inventory_capacity.
    Clamps between 0.0 and 1.0.
    """
    if not inventory_state or not isinstance(inventory_state, dict):
        _log_debug_event("ERROR", "InvalidInventoryState", "Inventory state missing or invalid.", debug_enabled=debug)
        return None

    used = inventory_state.get("used_capacity", 0)
    cap = inventory_state.get("inventory_capacity", 0)

    if not isinstance(used, (int, float)) or not isinstance(cap, (int, float)):
        _log_debug_event("ERROR", "InvalidCapacityValues", f"Invalid capacity values: used={used}, cap={cap}", debug_enabled=debug)
        return None

    if cap < 1:
        _log_debug_event("ERROR", "InvalidInventoryCapacity", f"Inventory capacity must be >= 1, got {cap}", debug_enabled=debug)
        return None

    pressure = float(used) / float(cap)
    pressure = max(0.0, min(1.0, pressure))
    
    return round(pressure, 4)

def validate_capacity_bounds(inventory_state, debug=False):
    """
    Validates that used_capacity does not exceed inventory_capacity for MVP.
    """
    if not inventory_state or not isinstance(inventory_state, dict):
        return {"ok": False, "error": "InvalidState"}

    used = inventory_state.get("used_capacity", 0)
    cap = inventory_state.get("inventory_capacity", 1)

    if used > cap:
        _log_debug_event("WARNING", "CapacityOverflow", f"Used capacity ({used}) exceeds total ({cap}).", debug_enabled=debug)
        return {"ok": False, "error": "CapacityOverflow", "message": f"Used capacity {used} exceeds capacity {cap}"}

    return {"ok": True}

def get_capacity_band(pressure):
    """Categorizes pressure into strategic bands."""
    if pressure is None:
        return "INVALID"
    
    if pressure == 0.0:
        return "EMPTY"
    elif pressure <= 0.25:
        return "LOW"
    elif pressure <= 0.60:
        return "MODERATE"
    elif pressure < 1.0:
        return "HIGH"
    elif pressure == 1.0:
        return "FULL"
    else:
        return "INVALID"

def summarize_capacity_pressure(inventory_state, debug=False):
    """
    Returns a structured summary of capacity pressure and strategic bands.
    """
    summary = {
        "ok": False,
        "inventory_id": None,
        "used_capacity": None,
        "inventory_capacity": None,
        "capacity_pressure": None,
        "capacity_band": "INVALID",
        "over_capacity": False,
        "error": None
    }

    if not inventory_state or not isinstance(inventory_state, dict):
        summary["error"] = {"message": "Invalid inventory state", "type": "InvalidState"}
        return summary

    summary["inventory_id"] = inventory_state.get("inventory_id")
    summary["used_capacity"] = inventory_state.get("used_capacity")
    summary["inventory_capacity"] = inventory_state.get("inventory_capacity")

    pressure = calculate_capacity_pressure(inventory_state, debug=debug)
    if pressure is None:
        summary["error"] = {"message": "Pressure calculation failed", "type": "CalculationError"}
        return summary

    summary["ok"] = True
    summary["capacity_pressure"] = pressure
    summary["capacity_band"] = get_capacity_band(pressure)
    
    bounds_check = validate_capacity_bounds(inventory_state, debug=debug)
    if not bounds_check["ok"]:
        summary["over_capacity"] = True
        # For MVP, over-capacity is considered INVALID strategic state
        summary["capacity_band"] = "INVALID"
        
    return summary

def apply_capacity_pressure_to_inventory_summary(inventory_state, summary=None, debug=False):
    """
    Enriches an existing inventory summary with capacity pressure data.
    """
    if summary is None:
        summary = {}

    pressure_data = summarize_capacity_pressure(inventory_state, debug=debug)
    
    if pressure_data["ok"]:
        summary["capacity_pressure"] = pressure_data["capacity_pressure"]
        summary["capacity_band"] = pressure_data["capacity_band"]
        summary["over_capacity"] = pressure_data["over_capacity"]
        summary["capacity_report"] = f"{pressure_data['used_capacity']}/{pressure_data['inventory_capacity']} ({pressure_data['capacity_band']})"
    else:
        summary["capacity_pressure_error"] = pressure_data.get("error")

    return summary
