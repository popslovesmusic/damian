import uuid

# Attempt to import debug_logger safely
try:
    from engine.debug.runtime import debug_logger
    _debug_logger_available = True
except ImportError:
    _debug_logger_available = False

# Inventory currency deduction
try:
    from engine.inventory.runtime import inventory_transaction_stub
    _inventory_available = True
except ImportError:
    _inventory_available = False

PATCH_ID = "TOWER-ENGINE-152"
SYSTEM_NAME = "foothold_recovery_stub"


def _log_debug_event(severity, event_type, message, context=None, debug_enabled=False):
    if _debug_logger_available and debug_enabled:
        try:
            event = debug_logger.make_debug_event(PATCH_ID, SYSTEM_NAME, severity, event_type, message, context)
            debug_logger.write_debug_event(event)
        except Exception:
            pass


def estimate_recovery_cost(claim, effort=1):
    """
    Estimates shard cost for a bounded recovery action.

    The Tower's pressure is preserved by scaling cost with:
    - current instability
    - claim status (OVERRUN is expensive to stabilize)
    """
    effort = max(1, int(effort))
    instability = float(claim.get("territorial_instability", 0.0) or 0.0)
    instability = max(0.0, min(1.0, instability))

    status = (claim.get("status", "ACTIVE") or "ACTIVE").upper()
    status_multiplier = 1.0
    if status == "DECAYING":
        status_multiplier = 1.2
    elif status == "OVERRUN":
        status_multiplier = 1.6

    # Base cost per effort is 2 shards, plus an instability premium.
    base = 2.0 * effort
    premium = (1.0 + (instability * 1.0)) * status_multiplier
    cost = int(round(base * premium))
    return max(1, cost)


def recover_foothold(claim, inventory_state, effort=1, debug=False):
    """
    Performs a bounded recovery action against a foothold.

    Effects (MVP):
    - spends Stability Shards
    - reduces territorial instability (but never to perfect safety)
    - can partially restore state if instability is reduced enough

    Non-goals:
    - free recovery
    - permanent safety
    - erasing collapse/scar history
    """
    if not _inventory_available:
        return {"ok": False, "error": "InventoryUnavailable", "message": "inventory_transaction_stub not available.", "payload": None}

    effort = max(1, int(effort))
    cost = estimate_recovery_cost(claim, effort=effort)

    inv_res = inventory_transaction_stub.deduct_inventory_currency(
        inventory_state, {"stability_shards": float(cost)}, debug=debug
    )
    if not inv_res.get("ok"):
        msg = inv_res.get("error", {}).get("message") or "Insufficient stability_shards."
        return {"ok": False, "error": "InsufficientResources", "message": msg, "payload": {"cost": cost}}

    prev_instability = float(claim.get("territorial_instability", 0.0) or 0.0)
    prev_instability = max(0.0, min(1.0, prev_instability))

    # Bounded reduction; high instability is harder to reduce.
    # Floor prevents perfect safety and consequence erasure.
    reduction = (0.06 * effort) + (max(0.0, 0.4 - prev_instability) * 0.02)
    new_instability = prev_instability - reduction
    new_instability = max(0.10, min(1.0, float(round(new_instability, 4))))

    previous_status = (claim.get("status", "ACTIVE") or "ACTIVE").upper()
    new_status = previous_status

    # Partial restoration gates; requires the player to push instability down.
    if previous_status == "OVERRUN" and new_instability <= 0.65:
        new_status = "DECAYING"
    if previous_status in ["DECAYING", "OVERRUN"] and new_instability <= 0.35:
        new_status = "ACTIVE"

    claim["territorial_instability"] = new_instability
    claim["instability_band"] = claim.get("instability_band", "ELEVATED")
    claim["status"] = new_status

    recovery_record = {
        "recovery_id": f"rec_{uuid.uuid4()}",
        "claim_id": claim.get("claim_id"),
        "effort": effort,
        "shards_spent": float(cost),
        "previous_instability": float(round(prev_instability, 4)),
        "new_instability": float(new_instability),
        "previous_status": previous_status,
        "new_status": new_status,
        "perfect_safety_prevented": True,
        "bounded_flags_clean": True
    }

    _log_debug_event(
        "INFO",
        "FootholdRecovered",
        f"Recovered {claim.get('claim_id')}: instability {prev_instability} -> {new_instability}",
        recovery_record,
        debug_enabled=debug,
    )

    return {
        "ok": True,
        "inventory_state": inv_res["inventory_state"],
        "inventory_transaction": inv_res.get("transaction"),
        "updated_claim": claim,
        "recovery_record": recovery_record,
        "summary": summarize_recovery(recovery_record),
        "error": None
    }


def summarize_recovery(record):
    if not record:
        return "No recovery record."
    return (
        f"Foothold Recovery [{record.get('claim_id', '')[:8]}]: "
        f"-{record.get('shards_spent', 0)} shards, "
        f"Instability {record.get('previous_instability', 0.0):.2f}->{record.get('new_instability', 0.0):.2f}, "
        f"State {record.get('previous_status')}->{record.get('new_status')}."
    )

