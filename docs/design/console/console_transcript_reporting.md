# Console Transcript Reporting

## Overview
The Console Transcript Reporter records manual playtest sessions as structured JSON evidence. These transcripts provide reviewable proof of system behavior, capturing every command executed and its corresponding result.

## Transcript Structure
Transcripts are stored in `outputs/console_transcripts/` and follow a strict schema to ensure all necessary evidence is captured for auditing.

### Key Fields
- **`transcript_id`**: A unique identifier for the playtest session.
- **`commands_requested`**: The sequence of commands provided to the harness.
- **`commands_executed`**: The sequence of commands that actually ran.
- **`command_results`**: The detailed output (payload, message, error) for each executed command.
- **`mutation_observed`**: Boolean flag indicating if a mutation was applied during the session.
- **`survivor_mark_observed`**: Boolean flag indicating if a survivor mark was attached or discovered.
- **`diff_observed`**: Boolean flag indicating if a floor diff report was generated.
- **`no_scope_creep_flags`**: Explicit confirmation that forbidden systems (combat, GPU, etc.) were not introduced.

## Usage
Transcripts can be generated programmatically using the `run_console_transcript` function:

```python
from engine.console.reports import console_transcript_reporter

commands = ["status", "ascend", "defeat", "diff", "quit"]
transcript = console_transcript_reporter.run_console_transcript(commands)
```

## Boundaries
- **Logical State Only**: Transcripts record logical state changes, not visual or performance data.
- **MVP Focus**: Observations are limited to the systems defined in the MVP (progression, residue, mutation, marks).
- **Static Artifacts**: Once written, transcripts are immutable records of a specific run.
