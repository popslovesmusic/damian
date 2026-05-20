# STAGE-018 Review — Territorial Instability & Foothold Collapse

Date: 2026-05-20

## Objective
Make domain footholds capable of degrading, destabilizing, and partially collapsing under Tower pressure while preserving:
- Recoverability (no unrecoverable dead states)
- Claim identity (claim records persist)
- Recursive consequence (pressure + scars feed forward)

This stage intentionally avoids any base-building runtime, housing, rendering, multiplayer sync, or real-time territory war.

## What Shipped (MVP)

### Territorial Instability (MVP Boundary + Stub)
- **Boundary:** `engine/domain/instability/territorial_instability_boundary.json`
- **Stub:** `engine/domain/instability/territorial_instability_stub.py`

Instability is a bounded [0..1] value per claim that:
- Increases under focused targeting and upkeep neglect
- Decreases under successful upkeep (recoverable)
- Does not delete or invalidate claim identity (`claim_id` persists)

### Foothold Collapse (MVP Boundary + Stub)
- **Boundary:** `engine/domain/collapse/foothold_collapse_boundary.json`
- **Stub:** `engine/domain/collapse/foothold_collapse_stub.py`

Collapse is derived evidence (not deletion):
- Begins only beyond an instability threshold
- Produces a bounded collapse level [0..1] and a band (`NONE|MINOR|PARTIAL|SEVERE`)
- Degrades *effective* benefits (e.g., recovery value) without erasing the claim
- Remains recoverable by lowering instability via maintenance

## Integration Points

### Domain Upkeep Integration
- `engine/domain/upkeep/domain_upkeep_stub.py` now:
  - Accepts an optional `targeting_record`
  - Merges targeting-based maintenance penalties into upkeep cost
  - Computes and persists `territorial_instability` on the claim when available

### Console / Dashboard Evidence (Read-Only Surfaces)
- Dashboard snapshot now includes `foothold_collapse_summary` for auditability.
- Console `status` surfaces:
  - Territorial instability peak + unstable count
  - Collapse peak + collapsed foothold count
- Console transcripts record both evidence fields from status payloads.

## Global Rules Check
- **Partial collapse, not deletion:** satisfied (collapse only degrades effective values).
- **Claim identity survives damage:** satisfied (claim remains in `domain_claims`; no deletion paths added).
- **Recoverability preserved:** satisfied (instability decreases with upkeep; collapse derived from instability).
- **Tower hostility increases without dead states:** satisfied (targeting/neglect drive instability upward).

## Known Gaps / Deferred to STAGE-019
- Active recovery actions (scar mitigation, repair operations, restoration costs)
- Persistence of collapse/instability history across runs as a first-class record type
- More granular benefit degradation (beyond recovery value) and claim-specific collapse traits

