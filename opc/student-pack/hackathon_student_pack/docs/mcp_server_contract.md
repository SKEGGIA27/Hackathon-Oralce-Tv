# Suggested MCP Server Contract

This file describes a recommended MCP tool surface for Task 1. Teams do not have to match these names exactly, but strong submissions should provide similar capabilities.

## Design Principles

- Each tool should do one clear job and return structured JSON.
- Tool outputs should be optimized for LLM consumption, not only for dashboards.
- Historical queries should allow both single-lap lookup and short analysis windows.
- Streaming should support deterministic replay from the provided JSONL file.

## Recommended Tools

### `get_session_overview`

Return high-level metadata, current stint information, latest lap, track status, tyre compound, and current position.

Example inputs:

- `session_name`

### `get_lap_window`

Return a list of lap records between `start_lap` and `end_lap`, inclusive.

Example inputs:

- `start_lap`
- `end_lap`
- `fields` optional list such as `lap_time_s`, `tires.wear_pct`, or `weather`

### `get_component_state`

Return the current or historical state of a specific subsystem.

Example inputs:

- `component` values such as `front_left_tire`, `brake_front_right`, `energy_system`
- `lap` optional single lap
- `last_n_laps` optional rolling window

### `compare_to_wear_model`

Return observed versus expected wear for one tyre or all tyres over a lap range.

Example inputs:

- `corner` values such as `front_left`
- `start_lap`
- `end_lap`

Recommended outputs:

- observed wear
- expected wear
- absolute gap in percentage points
- rolling wear-rate trend
- threshold status

### `get_strategy_context`

Return strategy-sensitive race information for a specific lap.

Example inputs:

- `lap`

Recommended outputs:

- laps remaining
- pit-loss estimate
- likely positions lost if pitting now
- projected finish position with and without stopping
- nearby gap information

### `list_race_control_events`

Return race-control messages such as safety-car periods, restarts, and local yellows.

### `stream_live_telemetry`

Replay the JSONL file one event at a time or in small batches.

Example inputs:

- `cursor`
- `batch_size`

Recommended outputs:

- events
- next cursor
- end-of-stream flag

## Suggested Acceptance Tests

1. Ask for the state of the front-left tyre at lap 23 and receive wear, temperature, pressure, and model deviation.
2. Ask whether the car should pit with 27 laps remaining and receive a strategy explanation with position impact.
3. Replay the stream through the safety-car phase and verify tool responses change over time.
4. Query race-control history and confirm the yellow-flag lap changes pace interpretation.
