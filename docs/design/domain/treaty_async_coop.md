# Treaty-Based Asynchronous Co-op Boundary

## Overview
Stage 041 defines the boundary for asynchronous cooperation in the Tower ecosystem. Survivors can form treaties between their domains to pool resources, share intelligence, and create joint defensive structures. This cooperation is designed to be beneficial but costly, increasing the "noise" and visibility of the involved domains.

## Treaty Boundary
The `engine/domain/contracts/treaty_boundary.json` defines the strict safety rules:
- **No Real-Time combat**: Cooperation is asynchronous. Players do not fight side-by-side in real-time.
- **Interdependence**: Shared rewards come with shared risks. Pressure spikes in one domain may bleed into treaty partners.
- **Traceable**: All treaties are governed by explicit contracts and recorded in audit logs.
- **Persistence Safe**: Dissolving a treaty never results in the loss of core player state or save data.

## Shared Pressure and Defense
Cooperation alters the pressure profile of a domain:
1. **Visibility Escalation**: Treaties increase the visibility of domains to the Tower, leading to more frequent adversarial encounters and environmental pressure.
2. **Joint Defense Echoes**: Domain Echoes can be reinforced by treaty partners, providing defensive bonuses that make them harder to attack asynchronously.
3. **Selective Pooling**: Only specific metrics (like visibility or route intelligence) are shared; core inventories and OS-level authority remain isolated.

## Terminal and Dashboard Integration
- **Admin Terminal**: Admins can use the `treaty status` and `treaty audit` commands to review active cooperation and its impact on system pressure.
- **Dashboard**: The domain dashboard displays active treaties and provides visual indicators of the "Visibility Penalty" incurred by cooperation.

## Conclusion
Treaty-based cooperation provides a strategic social layer for survivors. It encourages coordination and mutual support while strictly adhering to the Tower's asynchronous, authority-isolated architecture.
