# MVP Text Console Play Harness Runtime

## Overview
The MVP Text Console Play Harness provides a manual interface to exercise the core project loop. It integrates existing startup, outcome, progression, residue, mutation, survivor mark, and persistence systems into a single command-driven environment.

## Architecture
The console runtime is designed to be a thin wrapper around the existing `mvp_outcome_pipeline` and `mvp_startup_orchestrator`. It maintains a `session_state` that tracks the current `runtime_context` and any ephemeral data like the `latest_diff` report.

### Key Components
- **`start_console_session`**: Initializes the Project MVP environment.
- **`execute_console_command`**: Routes text commands to specific project systems.
- **`run_console_script`**: Allows batch execution of commands for automation and testing.

## Supported Commands
- `status`: Displays current floor, highest floor reached, total residues, mutation level, and unclaimed survivor marks.
- `ascend`: Triggers the `VICTORY_ASCEND` outcome, advancing the player to the next floor.
- `defeat`: Triggers the `DEFEAT_DROP` outcome, applying mutations and survivor marks to the landing floor and generating a diff report.
- `retreat`: Triggers the `RETREAT_TO_HUB` outcome.
- `diff`: Displays the `readable_summary` of the changes from the latest defeat.
- `marks`: Lists IDs of unclaimed survivor marks on the current floor.
- `claim <id>`: Discovers and claims a survivor mark, granting a reward.
- `save`: Persists the current `tower_state` to the local JSON save file.
- `quit`: Terminates the console session.
- `help`: Lists all available commands.

## Constraints and Boundaries
- **No Combat**: The console operates at the floor outcome level.
- **No Map Generation**: Floor transitions are logical and state-based.
- **No GPU/Rendering**: All output is text-based.
- **Safe Mode**: Commands fail safely if dependencies are missing or if invalid arguments are provided.
- **Audit-able**: All major actions are logged through the project's debug logging system.
