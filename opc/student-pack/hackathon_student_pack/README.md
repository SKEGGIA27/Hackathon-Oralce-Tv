# Formula Student AI Race Engineer Student Pack

This folder contains the student-facing materials for the hackathon. It is intended to be the only folder distributed to participants.

## What Is Included

- `docs/hackathon_brief.md`
  Challenge goals, deliverables, judging criteria, and the connected three-task scenario.
- `docs/mcp_server_contract.md`
  Suggested MCP tool surface for the telemetry platform.
- `telemetry/race_session_telemetry.json`
  Full race-session archive with metadata, race-control events, pit history, and all 50 lap snapshots.
- `telemetry/race_session_telemetry_stream.jsonl`
  One lap per line for deterministic replay and cursor-based streaming demos.
- `documents/fs_ai_endurance_regulations.pdf`
  Regulation handbook for the compliance RAG task.
- `documents/fs_ai_endurance_regulations.md`
  Text version of the regulation handbook for easier ingestion if needed.
- `documents/fs_e26_technical_dossier.pdf`
  Student-facing technical dossier for the car and experimental components.
- `documents/fs_e26_technical_dossier.md`
  Text version of the technical dossier for easier ingestion if needed.
- `presentations/formula-student-ai-race-engineer-briefing.pptx`
  Kickoff deck explaining the goals, scenario, dataset, and implementation hints.

## Recommended Student Workflow

1. Read `docs/hackathon_brief.md` first.
2. Use the telemetry files to build the MCP telemetry platform and anomaly-detection logic.
3. Use the regulations and technical dossier to build the compliance RAG system.
4. Combine both systems inside the conversational race engineer application.

## Notes

- The telemetry JSON and JSONL files describe the same race, but in different formats.
- The JSON file is best for full-session analysis.
- The JSONL file is best for live replay and streaming APIs.
- The document files are intentionally written for retrieval and citation tasks.
