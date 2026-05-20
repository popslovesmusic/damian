# Procedural Expansion Framework and Author Cartridge SDK

## Overview
Stage 053 defines the framework and SDK for third-party authors to create expansions for the Tower ecosystem. This system allows the community to build verifiable world cartridges, story modules, and procedural events while strictly maintaining the engine's asynchronous, decentralized, and safety-first architecture.

## SDK Boundary
The `engine/sdk/contracts/sdk_boundary.json` establishes the non-negotiable safety rules for all third-party content:
- **Strict Sandbox**: Expansions must operate within bounded parameters. Direct OS execution, host disk access, and remote code execution are strictly forbidden.
- **Hash Verification**: No cartridge can be loaded or executed without passing an integrity hash check against its manifest.
- **No Core Mutation**: Authors can expand the world context but cannot mutate the `TOWER_OS` core or override foundational safety boundaries.

## Expansion Contract
The expansion manifest (`engine/sdk/contracts/expansion_contract_schema.json`) defines what an author can include in a cartridge:
1. **Allowed Domains**: Narrative flavor, procedural contracts, market variants, and faction behaviors.
2. **Forbidden Domains**: Binary payloads, network overrides, and admin-level authority logic.
3. **Sandbox Permissions**: Explicit declarations of the subsystems the cartridge intends to interact with.

## SDK Manager
The `engine/sdk/runtime/sdk_manager.py` component acts as the gatekeeper for community content:
1. **Validation Pipeline**: Scans incoming cartridges against the schema, verifying hashes, rejecting unsafe payload extensions (e.g., `.sh`, `.exe`), and enforcing the forbidden domains list.
2. **API Bounding**: Provides stubs for narrative and contract generation that automatically cap rewards and enforce Tower identity (e.g., preventing unbounded currency generation).
3. **Publishing**: Simulates the packaging of a validated cartridge for distribution to the relay network.

## Terminal Integration
- **Admin Terminal**: Admins can use the `sdk validate` and `sdk audit` commands to review the status of incoming cartridges and monitor the history of published expansions.
- **Dashboard**: The player dashboard will reflect the presence of active expansions while clearly demarcating them as third-party modules.

## Conclusion
The Author Cartridge SDK ensures that Damian can grow through community contributions without sacrificing its identity or stability. By bounding expansions within a strict validation pipeline, the Tower remains a safe but deeply customizable environment.
