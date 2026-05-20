# MVP Domain Upkeep Boundary

This document defines the foundational rules for maintaining localized стратеги footholds (Domain Claims) in the Tower Engine.

## Philosophy: Order requires Maintenance

In the Tower, "Order" is an unnatural state. Once a player establishes a foothold (Recovery Anchor, Supply Cache, etc.), the Tower's natural entropy immediately begins to work against it. To maintain the strategic benefits of territory, players must materially invest resources to counteract this decay.

## Upkeep Mechanics

1.  **Stability Shard Drain**: Upkeep is paid using "Stability Shards" looted during runs. Each established claim has a specific upkeep cost per run.
2.  **State Decay**: If upkeep is not paid (either due to lack of resources or intentional neglect), the foothold begins to decay.
3.  **State Transitions**:
    *   **ACTIVE**: Full recovery value and strategic benefits.
    *   **DECAYING**: Reduced benefits. Increased visibility pressure.
    *   **OVERRUN**: Benefits lost. The foothold is effectively reclaimed by the Tower and may become a mutation hazard.

## Identity Rules

To maintain the engine's core strategic identity, upkeep follows these rules:

*   **No Safety Bypass**: Upkeep merely preserves a foothold; it does not protect the player from tactical combat risk or the consequences of a `DEFEAT_DROP`.
*   **Materiality**: Control requires the continuous expenditure of wealth. There is no such thing as "free order" in the Tower.
*   **Recursive Risk**: Decaying footholds attract **Reclamation Pressure**, increasing the likelihood of hazardous mutations in the surrounding area.

## Future Path

In Stage 015, this boundary will be implemented as a functional Upkeep Stub. Players will be able to execute `maintain` commands in the console, turning territory management into an active, resource-intensive strategic loop.
