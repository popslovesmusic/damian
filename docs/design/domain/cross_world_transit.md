# Cross-World Cartridge Transit and Survivor Identity Continuity

## Overview
Stage 043 defines the boundary for survivors transiting between different world cartridges (e.g., Damian, Jacob's Bane). This system ensures identity continuity—preserving a survivor's name, residue signature, and reputation—while allowing each world to reshape their physical expression and constraints.

## Transit Boundary
The `engine/domain/contracts/cross_world_transit_boundary.json` defines the strict safety rules:
- **Verified Import**: Survivors can only transit between verified world cartridges.
- **Identity Continuity**: All transit exports are hash-verified to prevent identity corruption.
- **Constraint Translation**: Direct binary state merging is prohibited. Each world must reinterpret the incoming survivor data through explicit translation modes.
- **Bounded Inventory**: Only symbolic "inventory echoes" (markers, tokens, residue artifacts) can travel between worlds; full inventory cloning is forbidden.

## Identity Continuity Contract
The identity contract (`engine/domain/contracts/identity_continuity_contract.json`) specifies the persistent and mutable components of a survivor:
1. **Persistent Components**: Survivor name, residue signature, trust markers, and treaty history remain constant across transits.
2. **Mutable Components**: Combat stats, resource capacity, and ability expressions are reshaped by the target world's rules.

## Transit Manager
The `engine/domain/transit_manager.py` component manages the transit lifecycle:
1. **Survivor Export**: Produces a hash-verified manifest summarizing the survivor's state for export.
2. **Residue Translation**: Performs lossy translation of residue profiles to match target world constraints (e.g., adapting residue weight).
3. **Inventory Echo Guard**: Filters incoming items to ensure only allowed transfer types (symbolic echoes) are imported.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `transit export` and `transit status` commands to manage and review survivor movements between world cartridges.
- **Dashboard**: The player dashboard displays evidence of their cross-world history and the "Residue Adaptation" they have undergone.

## Conclusion
The Cross-World Cartridge Transit system provides a secure and lore-compatible way for survivors to explore the broader Tower ecosystem. It ensures that while the survivor's essence remains continuous, the integrity and balance of each individual world are strictly preserved.
