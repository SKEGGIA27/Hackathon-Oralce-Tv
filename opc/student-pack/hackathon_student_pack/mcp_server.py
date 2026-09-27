"""
Formula Student AI Race Engineer — Telemetry Intelligence MCP Server
====================================================================

A FastAPI-based server implementing the MCP tool contract for telemetry
analysis of the STV-E26 endurance session at Vallelunga.

Tools exposed:
  1. get_session_overview    — session metadata, current stint, position
  2. get_lap_window          — lap records in a range with optional field filter
  3. get_component_state     — subsystem state (tyre, brakes, energy)
  4. get_strategy_context    — strategy info with pit recommendations
  5. compare_to_wear_model   — observed vs expected wear + anomaly detection
  6. list_race_control_events— safety car, flags, restarts
  7. stream_live_telemetry   — JSONL cursor-based replay

Security notes:
  - Listens on 127.0.0.1 only (localhost)
  - No user-controlled file paths; all data paths are hardcoded
  - Read-only: no writes, no database, no file uploads
  - Input validation via allow-lists for component names and lap ranges
  - TODO(security): Add API key auth if deployed beyond localhost
"""

import json
import os
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
TELEMETRY_JSON = BASE_DIR / "telemetry" / "race_session_telemetry.json"
TELEMETRY_JSONL = BASE_DIR / "telemetry" / "race_session_telemetry_stream.jsonl"


def _load_session_data() -> Dict[str, Any]:
    """Load the full session JSON into memory."""
    with open(TELEMETRY_JSON, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_stream_lines() -> List[Dict[str, Any]]:
    """Load all JSONL lines into a list for cursor-based replay."""
    lines: List[Dict[str, Any]] = []
    with open(TELEMETRY_JSONL, "r", encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if raw:
                lines.append(json.loads(raw))
    return lines


SESSION_DATA = _load_session_data()
STREAM_LINES = _load_stream_lines()
LAPS: List[Dict[str, Any]] = SESSION_DATA["laps"]
LAP_INDEX: Dict[int, Dict[str, Any]] = {lap["lap"]: lap for lap in LAPS}
TOTAL_LAPS = len(LAPS)

# ---------------------------------------------------------------------------
# Constants & Thresholds
# ---------------------------------------------------------------------------

VALID_COMPONENTS = {
    "front_left_tire", "front_right_tire", "rear_left_tire", "rear_right_tire",
    "brake_front_left", "brake_front_right", "brake_rear_left", "brake_rear_right",
    "energy_system",
}

CORNER_KEYS = ["front_left", "front_right", "rear_left", "rear_right"]

# Wear-gap thresholds (percentage points)
WEAR_THRESHOLD_NORMAL = 3.0
WEAR_THRESHOLD_ELEVATED = 8.0
WEAR_THRESHOLD_CRITICAL = 15.0
# Above critical = danger

# Operational wear limit (%) beyond which tyre is "out of window"
WEAR_LIMIT_OPERATIONAL = 80.0
WEAR_LIMIT_ABSOLUTE = 100.0

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="STV-E26 Telemetry MCP Server",
    description="MCP-compatible telemetry intelligence platform for Formula Student AI Race Engineer",
    version="1.0.0",
)

# Allow CORS for local development (Task 3 web app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000",
                   "http://localhost:8501", "http://127.0.0.1:8501",
                   "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_wear_gap(gap_pp: float) -> str:
    """Classify wear deviation into threshold status."""
    if gap_pp < WEAR_THRESHOLD_NORMAL:
        return "normal"
    elif gap_pp < WEAR_THRESHOLD_ELEVATED:
        return "elevated"
    elif gap_pp < WEAR_THRESHOLD_CRITICAL:
        return "critical"
    else:
        return "danger"


def _project_laps_to_limit(current_wear: float, deg_rate: float, limit: float) -> Optional[float]:
    """Estimate how many laps until a wear limit is reached."""
    if deg_rate <= 0:
        return None
    remaining = limit - current_wear
    if remaining <= 0:
        return 0.0
    return round(remaining / deg_rate, 1)


def _get_lap_or_404(lap: int) -> Dict[str, Any]:
    """Return lap data or raise HTTP 404."""
    if lap not in LAP_INDEX:
        raise HTTPException(
            status_code=404,
            detail=f"Lap {lap} not found. Valid range: 1-{TOTAL_LAPS}."
        )
    return LAP_INDEX[lap]


def _validate_lap_range(start_lap: int, end_lap: int) -> None:
    """Validate that start/end are within bounds."""
    if start_lap < 1 or end_lap > TOTAL_LAPS:
        raise HTTPException(
            status_code=400,
            detail=f"Lap range must be between 1 and {TOTAL_LAPS}."
        )
    if start_lap > end_lap:
        raise HTTPException(
            status_code=400,
            detail="start_lap must be <= end_lap."
        )


def _filter_fields(record: Dict[str, Any], fields: Optional[List[str]]) -> Dict[str, Any]:
    """If fields list provided, return only those top-level keys + always include lap."""
    if not fields:
        return record
    result = {"lap": record.get("lap")}
    for f in fields:
        # Support dotted paths like "tires.wear_pct"
        parts = f.split(".")
        val = record
        for p in parts:
            if isinstance(val, dict) and p in val:
                val = val[p]
            else:
                val = None
                break
        result[f] = val
    return result


def _extract_component_data(lap_data: Dict[str, Any], component: str) -> Dict[str, Any]:
    """Extract subsystem-specific data from a lap record."""
    result: Dict[str, Any] = {"lap": lap_data["lap"], "component": component}

    if component.endswith("_tire"):
        # Map component name to corner key
        corner = component.replace("_tire", "")
        tires = lap_data.get("tires", {})
        result["compound"] = tires.get("compound")
        result["temperature_c"] = tires.get("temperature_c", {}).get(corner)
        result["pressure_bar"] = tires.get("pressure_bar", {}).get(corner)
        result["wear_pct"] = tires.get("wear_pct", {}).get(corner)
        result["expected_wear_pct"] = tires.get("expected_wear_pct", {}).get(corner)
        result["degradation_rate_pct_per_lap"] = tires.get("degradation_rate_pct_per_lap", {}).get(corner)

        observed = result.get("wear_pct")
        expected = result.get("expected_wear_pct")
        if observed is not None and expected is not None:
            gap = round(observed - expected, 2)
            result["wear_gap_pp"] = gap
            result["threshold_status"] = _classify_wear_gap(abs(gap))

        deg_rate = result.get("degradation_rate_pct_per_lap")
        if observed is not None and deg_rate is not None:
            result["projected_laps_to_80pct"] = _project_laps_to_limit(observed, deg_rate, WEAR_LIMIT_OPERATIONAL)
            result["projected_laps_to_100pct"] = _project_laps_to_limit(observed, deg_rate, WEAR_LIMIT_ABSOLUTE)

    elif component.startswith("brake_"):
        # Map e.g. "brake_front_left" -> "front_left"
        corner = component.replace("brake_", "")
        result["temperature_c"] = lap_data.get("brake_temperatures_c", {}).get(corner)

    elif component == "energy_system":
        result.update(lap_data.get("energy_system", {}))

    return result


# ---------------------------------------------------------------------------
# Tool 1: get_session_overview
# ---------------------------------------------------------------------------

@app.get("/tools/get_session_overview")
def get_session_overview(
    session_name: Optional[str] = Query(None, description="Session name filter (ignored, single session)")
) -> Dict[str, Any]:
    """
    Return high-level session metadata, current stint, latest lap,
    track status, tyre compound, and current position.
    """
    metadata = SESSION_DATA.get("session_metadata", {})
    latest_lap = LAPS[-1]
    pit_history = SESSION_DATA.get("pit_stop_history", [])

    # Determine current stint info from latest lap
    return {
        "session_metadata": metadata,
        "schema_version": SESSION_DATA.get("schema_version"),
        "field_notes": SESSION_DATA.get("field_notes", []),
        "total_laps_completed": TOTAL_LAPS,
        "latest_lap": {
            "lap": latest_lap["lap"],
            "lap_time_s": latest_lap["lap_time_s"],
            "position": latest_lap["position"],
            "track_status": latest_lap["track_status"],
            "stint_number": latest_lap["stint_number"],
            "stint_lap": latest_lap["stint_lap"],
        },
        "current_compound": latest_lap.get("tires", {}).get("compound"),
        "pit_stops_made": len(pit_history),
        "pit_stop_history": pit_history,
    }


# ---------------------------------------------------------------------------
# Tool 2: get_lap_window
# ---------------------------------------------------------------------------

@app.get("/tools/get_lap_window")
def get_lap_window(
    start_lap: int = Query(..., ge=1, description="First lap of the window (inclusive)"),
    end_lap: int = Query(..., ge=1, description="Last lap of the window (inclusive)"),
    fields: Optional[str] = Query(None, description="Comma-separated field paths to include, e.g. 'lap_time_s,tires.wear_pct,weather'"),
) -> Dict[str, Any]:
    """
    Return a list of lap records between start_lap and end_lap inclusive.
    Optionally filter to specific fields.
    """
    _validate_lap_range(start_lap, end_lap)

    field_list = [f.strip() for f in fields.split(",")] if fields else None

    laps_out = []
    for lap_num in range(start_lap, end_lap + 1):
        lap_data = LAP_INDEX.get(lap_num)
        if lap_data:
            laps_out.append(_filter_fields(lap_data, field_list))

    return {
        "start_lap": start_lap,
        "end_lap": end_lap,
        "count": len(laps_out),
        "fields_filter": field_list,
        "laps": laps_out,
    }


# ---------------------------------------------------------------------------
# Tool 3: get_component_state
# ---------------------------------------------------------------------------

@app.get("/tools/get_component_state")
def get_component_state(
    component: str = Query(..., description="Subsystem name, e.g. front_left_tire, brake_front_right, energy_system"),
    lap: Optional[int] = Query(None, ge=1, description="Single lap to query"),
    last_n_laps: Optional[int] = Query(None, ge=1, le=50, description="Rolling window of N most recent laps"),
) -> Dict[str, Any]:
    """
    Return the state of a specific subsystem at a given lap or over a window.
    """
    if component not in VALID_COMPONENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown component '{component}'. Valid: {sorted(VALID_COMPONENTS)}"
        )

    if lap is not None:
        lap_data = _get_lap_or_404(lap)
        return {
            "component": component,
            "mode": "single_lap",
            "data": _extract_component_data(lap_data, component),
        }

    if last_n_laps is not None:
        # Last N laps from the end of the session
        start = max(1, TOTAL_LAPS - last_n_laps + 1)
        records = []
        for ln in range(start, TOTAL_LAPS + 1):
            ld = LAP_INDEX.get(ln)
            if ld:
                records.append(_extract_component_data(ld, component))
        return {
            "component": component,
            "mode": "rolling_window",
            "window_size": last_n_laps,
            "data": records,
        }

    # Default: return latest lap
    latest = LAPS[-1]
    return {
        "component": component,
        "mode": "latest",
        "data": _extract_component_data(latest, component),
    }


# ---------------------------------------------------------------------------
# Tool 4: compare_to_wear_model
# ---------------------------------------------------------------------------

@app.get("/tools/compare_to_wear_model")
def compare_to_wear_model(
    corner: Optional[str] = Query(None, description="Tyre corner: front_left, front_right, rear_left, rear_right. Omit for all."),
    start_lap: int = Query(..., ge=1, description="Start lap"),
    end_lap: int = Query(..., ge=1, description="End lap"),
) -> Dict[str, Any]:
    """
    Compare observed vs expected tyre wear over a lap range.
    Returns per-corner analysis with gap, trend, and anomaly classification.
    """
    _validate_lap_range(start_lap, end_lap)

    corners = [corner] if corner else CORNER_KEYS
    for c in corners:
        if c not in CORNER_KEYS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown corner '{c}'. Valid: {CORNER_KEYS}"
            )

    analysis: Dict[str, Any] = {}

    for c in corners:
        lap_details = []
        deg_rates = []
        max_gap = 0.0
        max_gap_lap = start_lap

        for lap_num in range(start_lap, end_lap + 1):
            ld = LAP_INDEX.get(lap_num)
            if not ld:
                continue
            tires = ld.get("tires", {})
            observed = tires.get("wear_pct", {}).get(c)
            expected = tires.get("expected_wear_pct", {}).get(c)
            deg_rate = tires.get("degradation_rate_pct_per_lap", {}).get(c)

            if observed is None or expected is None:
                continue

            gap = round(observed - expected, 2)
            abs_gap = abs(gap)

            if abs_gap > max_gap:
                max_gap = abs_gap
                max_gap_lap = lap_num

            if deg_rate is not None:
                deg_rates.append(deg_rate)

            entry = {
                "lap": lap_num,
                "observed_wear_pct": observed,
                "expected_wear_pct": expected,
                "gap_pp": gap,
                "threshold_status": _classify_wear_gap(abs_gap),
                "degradation_rate": deg_rate,
            }

            # Projections for current lap
            if deg_rate and deg_rate > 0:
                entry["projected_laps_to_80pct"] = _project_laps_to_limit(observed, deg_rate, WEAR_LIMIT_OPERATIONAL)
                entry["projected_laps_to_100pct"] = _project_laps_to_limit(observed, deg_rate, WEAR_LIMIT_ABSOLUTE)

            lap_details.append(entry)

        # Trend analysis
        trend = "stable"
        if len(deg_rates) >= 3:
            first_half = deg_rates[:len(deg_rates) // 2]
            second_half = deg_rates[len(deg_rates) // 2:]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            delta = avg_second - avg_first
            if delta > 0.3:
                trend = "rapidly_increasing"
            elif delta > 0.1:
                trend = "increasing"
            elif delta < -0.1:
                trend = "decreasing"

        # Latest state for summary
        latest = lap_details[-1] if lap_details else {}
        final_status = latest.get("threshold_status", "unknown")

        # Build recommendation
        recommendation = None
        if final_status == "danger":
            recommendation = (
                f"CRITICAL: {c} tyre wear deviation is {latest.get('gap_pp', 0):.1f}pp above model. "
                f"Degradation rate {latest.get('degradation_rate', 0):.2f}%/lap is unsustainable. "
                f"Pit stop strongly recommended within the next 1-2 laps to avoid tyre failure."
            )
        elif final_status == "critical":
            laps_to_80 = latest.get("projected_laps_to_80pct")
            recommendation = (
                f"WARNING: {c} tyre wear gap at {latest.get('gap_pp', 0):.1f}pp and rising. "
                f"Estimated {laps_to_80 if laps_to_80 else '?'} laps to operational limit. "
                f"Prepare for pit stop within next 3-5 laps."
            )
        elif final_status == "elevated":
            recommendation = (
                f"MONITOR: {c} tyre showing elevated wear deviation of {latest.get('gap_pp', 0):.1f}pp. "
                f"Continue monitoring; situation could escalate."
            )

        analysis[c] = {
            "corner": c,
            "lap_range": [start_lap, end_lap],
            "max_gap_pp": round(max_gap, 2),
            "max_gap_at_lap": max_gap_lap,
            "current_status": final_status,
            "degradation_trend": trend,
            "recommendation": recommendation,
            "lap_details": lap_details,
        }

    # Overall summary
    worst_corner = max(analysis.values(), key=lambda x: x["max_gap_pp"])
    return {
        "analysis": analysis,
        "worst_corner": worst_corner["corner"],
        "worst_gap_pp": worst_corner["max_gap_pp"],
        "overall_status": worst_corner["current_status"],
    }


# ---------------------------------------------------------------------------
# Tool 5: get_strategy_context
# ---------------------------------------------------------------------------

@app.get("/tools/get_strategy_context")
def get_strategy_context(
    lap: int = Query(..., ge=1, description="Lap number to evaluate strategy for"),
) -> Dict[str, Any]:
    """
    Return strategy-sensitive race information including pit recommendation,
    wear projection, and position impact analysis.
    """
    lap_data = _get_lap_or_404(lap)
    strategy = lap_data.get("strategy_context", {})
    tires = lap_data.get("tires", {})
    race_ctx = lap_data.get("race_context", {})

    # Wear projection for each corner
    wear_projection: Dict[str, Any] = {}
    laps_remaining = strategy.get("laps_remaining", 0)

    for c in CORNER_KEYS:
        current_wear = tires.get("wear_pct", {}).get(c, 0)
        deg_rate = tires.get("degradation_rate_pct_per_lap", {}).get(c, 0)
        expected_wear = tires.get("expected_wear_pct", {}).get(c, 0)
        gap = round(current_wear - expected_wear, 2)

        projected_end_wear = round(current_wear + deg_rate * laps_remaining, 1)
        laps_to_80 = _project_laps_to_limit(current_wear, deg_rate, WEAR_LIMIT_OPERATIONAL)
        laps_to_100 = _project_laps_to_limit(current_wear, deg_rate, WEAR_LIMIT_ABSOLUTE)

        wear_projection[c] = {
            "current_wear_pct": current_wear,
            "expected_wear_pct": expected_wear,
            "gap_pp": gap,
            "deg_rate_per_lap": deg_rate,
            "projected_end_of_stint_wear_pct": projected_end_wear,
            "exceeds_operational_limit": projected_end_wear > WEAR_LIMIT_OPERATIONAL,
            "laps_to_operational_limit": laps_to_80,
            "laps_to_absolute_limit": laps_to_100,
        }

    # Generate pit recommendation
    pit_window = strategy.get("pit_window_status", "closed")
    recommendation = _generate_pit_recommendation(
        pit_window, wear_projection, laps_remaining, strategy, race_ctx
    )

    return {
        "lap": lap,
        "strategy_context": strategy,
        "race_context": race_ctx,
        "current_compound": tires.get("compound"),
        "driver_feedback": lap_data.get("driver_feedback"),
        "wear_projection": wear_projection,
        "pit_recommendation": recommendation,
    }


def _generate_pit_recommendation(
    pit_window: str,
    wear_proj: Dict[str, Any],
    laps_remaining: int,
    strategy: Dict[str, Any],
    race_ctx: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate a structured pit stop recommendation."""

    # Find worst corner
    worst_corner = None
    worst_gap = 0.0
    worst_laps_to_limit = float("inf")

    for c, proj in wear_proj.items():
        gap = abs(proj.get("gap_pp", 0))
        laps_to_limit = proj.get("laps_to_operational_limit")

        if gap > worst_gap:
            worst_gap = gap
            worst_corner = c

        if laps_to_limit is not None and laps_to_limit < worst_laps_to_limit:
            worst_laps_to_limit = laps_to_limit

    # Decision logic
    if pit_window == "urgent" or worst_gap >= WEAR_THRESHOLD_CRITICAL:
        action = "PIT_NOW"
        urgency = "critical"
        reasoning = (
            f"The {worst_corner} tyre has a wear deviation of {worst_gap:.1f}pp from the model. "
            f"At current degradation rate, the operational limit (80%) will be reached in "
            f"approximately {worst_laps_to_limit:.0f} laps. With {laps_remaining} laps remaining, "
            f"continuing without a stop risks tyre failure and significant position loss. "
            f"Estimated pit loss: {strategy.get('estimated_pit_loss_s', '?')}s "
            f"({strategy.get('estimated_positions_lost_if_pit_now', '?')} positions). "
            f"Projected finish P{strategy.get('projected_finish_position_if_pit_now', '?')} if pitting now "
            f"vs P{strategy.get('projected_finish_position_if_no_stop', '?')} if staying out (with declining pace)."
        )
    elif pit_window == "open" or worst_gap >= WEAR_THRESHOLD_ELEVATED:
        action = "PIT_SOON"
        urgency = "elevated"
        reasoning = (
            f"The {worst_corner} tyre is showing elevated wear deviation ({worst_gap:.1f}pp). "
            f"Pit window is open. Recommend planning a stop within the next 3-5 laps. "
            f"Current gap to car ahead: {race_ctx.get('gap_to_car_ahead_s', '?')}s, "
            f"gap behind: {race_ctx.get('gap_to_car_behind_s', '?')}s."
        )
    elif pit_window == "monitor":
        action = "MONITOR"
        urgency = "watch"
        reasoning = (
            f"Wear deviation on {worst_corner} is {worst_gap:.1f}pp — within monitoring range. "
            f"Continue and reassess in 2-3 laps."
        )
    else:
        action = "STAY_OUT"
        urgency = "normal"
        reasoning = (
            f"All tyres within normal operating window. Wear gap on worst corner "
            f"({worst_corner}) is {worst_gap:.1f}pp. No action required."
        )

    return {
        "action": action,
        "urgency": urgency,
        "worst_corner": worst_corner,
        "worst_gap_pp": round(worst_gap, 2),
        "laps_to_operational_limit": round(worst_laps_to_limit, 1) if worst_laps_to_limit != float("inf") else None,
        "reasoning": reasoning,
    }


# ---------------------------------------------------------------------------
# Tool 6: list_race_control_events
# ---------------------------------------------------------------------------

@app.get("/tools/list_race_control_events")
def list_race_control_events(
    event_type: Optional[str] = Query(None, description="Filter by type: safety_car, restart, yellow_flag"),
) -> Dict[str, Any]:
    """
    Return race-control messages: safety car, restarts, local yellows.
    """
    events = SESSION_DATA.get("race_control_events", [])

    if event_type:
        valid_types = {"safety_car", "restart", "yellow_flag"}
        if event_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown event type '{event_type}'. Valid: {sorted(valid_types)}"
            )
        events = [e for e in events if e.get("type") == event_type]

    return {
        "total_events": len(events),
        "events": events,
    }


# ---------------------------------------------------------------------------
# Tool 7: stream_live_telemetry
# ---------------------------------------------------------------------------

@app.get("/tools/stream_live_telemetry")
def stream_live_telemetry(
    cursor: int = Query(0, ge=0, description="Zero-based cursor position in the JSONL stream"),
    batch_size: int = Query(1, ge=1, le=10, description="Number of events to return per call"),
) -> Dict[str, Any]:
    """
    Replay the JSONL file one event at a time or in small batches.
    Returns events, next cursor, and end-of-stream flag.
    """
    total = len(STREAM_LINES)

    if cursor >= total:
        return {
            "events": [],
            "next_cursor": total,
            "end_of_stream": True,
            "total_events": total,
        }

    end = min(cursor + batch_size, total)
    events = STREAM_LINES[cursor:end]

    return {
        "events": events,
        "next_cursor": end,
        "end_of_stream": end >= total,
        "total_events": total,
    }


# ---------------------------------------------------------------------------
# Tool discovery endpoint (MCP-style)
# ---------------------------------------------------------------------------

@app.get("/tools")
def list_tools() -> Dict[str, Any]:
    """List all available MCP tools with their descriptions and parameters."""
    return {
        "tools": [
            {
                "name": "get_session_overview",
                "description": "Return high-level session metadata, current stint, latest lap, track status, tyre compound, and position.",
                "endpoint": "/tools/get_session_overview",
                "method": "GET",
                "parameters": {
                    "session_name": {"type": "string", "required": False, "description": "Session name (optional)"}
                },
            },
            {
                "name": "get_lap_window",
                "description": "Return lap records between start_lap and end_lap inclusive, with optional field filtering.",
                "endpoint": "/tools/get_lap_window",
                "method": "GET",
                "parameters": {
                    "start_lap": {"type": "integer", "required": True, "description": "First lap (inclusive)"},
                    "end_lap": {"type": "integer", "required": True, "description": "Last lap (inclusive)"},
                    "fields": {"type": "string", "required": False, "description": "Comma-separated field paths"},
                },
            },
            {
                "name": "get_component_state",
                "description": "Return state of a specific subsystem (tyre, brake, energy) at a given lap or over a window.",
                "endpoint": "/tools/get_component_state",
                "method": "GET",
                "parameters": {
                    "component": {"type": "string", "required": True, "description": "e.g. front_left_tire, brake_front_right, energy_system"},
                    "lap": {"type": "integer", "required": False, "description": "Single lap"},
                    "last_n_laps": {"type": "integer", "required": False, "description": "Rolling window"},
                },
            },
            {
                "name": "compare_to_wear_model",
                "description": "Compare observed vs expected tyre wear with gap analysis, trend detection, and anomaly classification.",
                "endpoint": "/tools/compare_to_wear_model",
                "method": "GET",
                "parameters": {
                    "corner": {"type": "string", "required": False, "description": "front_left, front_right, rear_left, rear_right"},
                    "start_lap": {"type": "integer", "required": True},
                    "end_lap": {"type": "integer", "required": True},
                },
            },
            {
                "name": "get_strategy_context",
                "description": "Return strategy info with pit recommendation, wear projection, and position impact.",
                "endpoint": "/tools/get_strategy_context",
                "method": "GET",
                "parameters": {
                    "lap": {"type": "integer", "required": True, "description": "Lap to evaluate"},
                },
            },
            {
                "name": "list_race_control_events",
                "description": "Return race-control messages: safety car, flags, restarts.",
                "endpoint": "/tools/list_race_control_events",
                "method": "GET",
                "parameters": {
                    "event_type": {"type": "string", "required": False, "description": "safety_car, restart, yellow_flag"},
                },
            },
            {
                "name": "stream_live_telemetry",
                "description": "Replay JSONL stream with cursor-based pagination.",
                "endpoint": "/tools/stream_live_telemetry",
                "method": "GET",
                "parameters": {
                    "cursor": {"type": "integer", "required": False, "default": 0},
                    "batch_size": {"type": "integer", "required": False, "default": 1},
                },
            },
        ]
    }


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "laps_loaded": TOTAL_LAPS,
        "stream_events": len(STREAM_LINES),
        "session": SESSION_DATA.get("session_metadata", {}).get("session_name"),
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="127.0.0.1", port=8100, log_level="info")
