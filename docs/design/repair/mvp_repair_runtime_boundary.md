# MVP Repair Runtime Boundary

This document defines the foundational framework for bounded equipment repair in the Tower Engine.

## Philosophy: Material Cost for Strategic Restoration

In the Tower Engine, repair is not a "free" or automatic process. It is a material conversion where the player's accumulated resources (Stage 008) are used to mitigate the deterioration caused by the Tower (Stage 009):

1.  **Material Demand**: Repairing equipment requires the consumption of specific repair materials from the player's inventory. This creates a strategic strategic loop between wealth generation (loot) and gear condition.
2.  **Bounded Restoration**: Gear condition is restored in predictable, bounded increments. It cannot be repaired beyond its maximum structural limit.
3.  **Audit Recording**: Every repair attempt, whether successful or failed due to insufficient materials, produces a structured `RepairEvent`. This provides a material audit trail for the game's net economy.

## Runtime Responsibilities

*   **Consuming Materials**: Mechanically deduct the required items from the inventory using atomic transactions.
*   **Restoring Condition**: Update current durability based on the material used, ensuring it remains within maximum bounds.
*   **Safe Failure**: If the player lacks the required materials, the repair fails safely without modifying the gear or corrupting the inventory.
*   **Reporting**: Every event must report the amount restored and the materials consumed to ensure economic observability.

## Identity Rules (Consequence Preservation)

To maintain engine integrity, the repair system follows these strict rules:

*   **No Defeat Cancellation**: Having the ability to repair gear cannot prevent the consequences of `DEFEAT_DROP`.
*   **No Residue Bypass**: Maintaining gear condition does not prevent the generation of residue from player actions.
*   **No Free Upkeep**: Repair must always carry a material cost; there is no "infinite durability" or maintenance-free high-power gear in the MVP.
*   **No Invulnerability**: Restoring gear condition does not grant the player temporary or permanent invulnerability.

## Future Path

In future patches, this boundary will be implemented as a functional runtime. The existing `repair` console command will be updated to trigger this runtime, materially connecting the player's material inventory to their operational combat effectiveness.
