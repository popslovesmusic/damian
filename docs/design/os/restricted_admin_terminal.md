# Restricted Admin Terminal Prototype

## Overview
Stage 031 establishes a bounded maintenance interface for the Tower OS. This terminal is designed as a "maintenance hatch," providing diagnostics and system status without exposing a general-purpose Linux shell.

## Terminal Boundary
The `engine/os_boundary/contracts/restricted_terminal_boundary.json` defines strict security rules:
- **No Unrestricted Shell**: Access to standard shells (bash, sh) is prohibited.
- **No Sudo Escape**: Commands requiring root elevation are forbidden.
- **Strict Allowlisting**: Only commands defined in the command contract can be executed.
- **Data Isolation**: Any writes (like audit logs) must target the `TOWER_DATA` partition.

## Command Contract and Registry
The terminal uses an allowlist-based command registry (`engine/os_boundary/restricted_terminal.py`) governed by `engine/os_boundary/contracts/admin_terminal_command_contract.json`. 

### Supported Command Families
- `status`: General Tower OS and engine health.
- `persistence`: Details on `TOWER_DATA` mount and persistence layer integrity.
- `diagnostics`: System health checks (RootFS integrity, resource pressure).
- `logs`: Access to maintenance and engine logs.
- `exit`: Graceful closure of the terminal interface.

## Security Features
1. **Input Sanitization**: Commands are validated for length and disallowed characters (pipe, semicolon, etc.) to prevent command injection.
2. **Audit Logging**: Every command attempt—whether successful, rejected, or unknown—is logged to a persistent audit file on `TOWER_DATA`.
3. **Safe Dispatching**: Command execution is handled by internal Python methods rather than sub-shell execution, eliminating shell escape vectors.

## Conclusion
The restricted admin terminal provides a lore-compatible and secure method for system maintenance. It ensures that even under diagnostic scenarios, the Tower OS maintains its integrity and host safety boundaries.
