# STAGE-019 Review — Foothold Recovery & Scar Mitigation

Date: 2026-05-20

## Objective
Give players bounded tools to:
- Stabilize damaged footholds (reduce instability / restore partial function)
- Mitigate mutation scar pressure (reduce pressure, not erase history)

Without introducing:
- Permanent safe zones
- Total scar erasure
- Free recovery
- Base-building runtime, rendering, multiplayer sync, or real-time territory war

## What Shipped (MVP)

### Foothold Recovery (Boundary + Stub)
- Boundary: `engine/domain/recovery/foothold_recovery_boundary.json`
- Stub: `engine/domain/recovery/foothold_recovery_stub.py`

Recovery action properties:
- Costs **Stability Shards** (material, bounded)
- Reduces `territorial_instability` in **bounded steps**
- Prevents “perfect safety” by enforcing a minimum instability floor
- Allows **partial state restoration** (`OVERRUN -> DECAYING -> ACTIVE`) gated by instability thresholds

### Scar Mitigation (Boundary + Stub)
- Boundary: `engine/residue/mutation/scar_mitigation_boundary.json`
- Stub: `engine/residue/mutation/scar_mitigation_stub.py`

Mitigation properties:
- Costs **Stability Shards**
- Produces bounded mitigation credit applied during upkeep/targeting
- Enforces a minimum scarring floor (`>= 0.10`) to prevent total erasure

## Integrations

### Upkeep Integration (Mitigation Affects Pressure)
`maintain` now applies mitigation credit to the node’s scarring record before computing claim targeting. This reduces pressure (targeting) without deleting scars or changing claim identity.

### Dashboard Evidence (Recovery)
Domain dashboard snapshots now include `foothold_recovery_summary`, surfacing:
- Recovery actions taken
- Total shards spent
- Restoration counts (from overrun / to active)

### Console Commands
Added commands:
- `recover CLAIM_ID [EFFORT]` — spends shards, reduces instability, may restore state
- `mitigate NODE_ID [EFFORT]` — spends shards, increases mitigation credit for current floor+node

### Console Transcripts
Transcripts record:
- Recovery actions observed + shard spend + summaries
- Mitigation actions observed + shard spend + highest credit observed

## Global Rules Check
- No permanent safe zones: satisfied (bounded floors, no safety bypass)
- No total scar erasure: satisfied (minimum scar floor enforced)
- No free recovery: satisfied (shards are deducted for both actions)
- Tower hostility preserved: satisfied (cost scaling + bounded limits; scarring still persists)

## Known Gaps / Deferred
- Persistence of mitigation credits across runs as a first-class record
- More nuanced recovery burden (e.g., temporary upkeep premium after recovery)
- Player-facing guidance for choosing mitigation vs. recovery under targeting pressure

