import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

DATA_DIR = Path(__file__).parent / "data"

#mcp = FastMCP("F1 Hackathon Server")

mcp = FastMCP(
    "F1 Hackathon Server",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

def _load_json(name: str) -> Any:
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _latest_laps() -> List[Dict[str, Any]]:
    return _load_json("lap_times.json")


@mcp.tool()
def get_session_overview() -> Dict[str, Any]:
    """Return a short summary of the current session."""
    meta = _load_json("session_metadata.json")
    laps = _latest_laps()
    events = _load_json("race_events.json")
    return {
        "session_id": meta["session_id"],
        "season": meta["season"],
        "circuit": meta["circuit"],
        "session_type": meta["session_type"],
        "laps": meta["laps"],
        "lap_rows": len(laps),
        "events_count": len(events),
    }


@mcp.tool()
def get_driver_position(driver_id: str, lap: Optional[int] = None) -> Dict[str, Any]:
    """Return a driver's position on a given lap, or the latest known lap."""
    laps = _latest_laps()
    driver_laps = [row for row in laps if row["driver_id"] == driver_id]

    if not driver_laps:
        return {"driver_id": driver_id, "found": False}

    if lap is None:
        row = max(driver_laps, key=lambda x: x["lap"])
    else:
        matches = [row for row in driver_laps if row["lap"] == lap]
        if not matches:
            return {"driver_id": driver_id, "lap": lap, "found": False}
        row = matches[0]

    return {
        "driver_id": driver_id,
        "found": True,
        "lap": row["lap"],
        "position": row["position"],
        "gap_to_leader_ms": row["gap_to_leader_ms"],
        "lap_time_ms": row["lap_time_ms"],
        "tire_compound": row["tire_compound"],
        "tire_age": row["tire_age"],
    }


@mcp.tool()
def compare_drivers(driver_a: str, driver_b: str, lap_start: int, lap_end: int) -> Dict[str, Any]:
    """Compare average lap time between two drivers over a lap range."""
    laps = _latest_laps()

    def avg_lap_time(driver_id: str) -> Optional[float]:
        rows = [
            row["lap_time_ms"]
            for row in laps
            if row["driver_id"] == driver_id and lap_start <= row["lap"] <= lap_end
        ]
        return round(sum(rows) / len(rows), 2) if rows else None

    a = avg_lap_time(driver_a)
    b = avg_lap_time(driver_b)

    return {
        "driver_a": driver_a,
        "driver_b": driver_b,
        "lap_start": lap_start,
        "lap_end": lap_end,
        "avg_lap_time_ms": {
            driver_a: a,
            driver_b: b,
        },
        "faster_driver": driver_a if a is not None and b is not None and a < b else driver_b if a is not None and b is not None and b < a else None,
    }


@mcp.tool()
def recommend_strategy(driver_id: str) -> Dict[str, Any]:
    """Return a simple pit-strategy recommendation based on tire age and weather."""
    laps = _latest_laps()
    weather = _load_json("weather.json")
    driver_rows = [row for row in laps if row["driver_id"] == driver_id]

    if not driver_rows:
        return {"driver_id": driver_id, "found": False}

    latest = max(driver_rows, key=lambda x: x["lap"])
    latest_weather = max(weather, key=lambda x: x["lap"])

    recommendation = "stay_out"
    reason = "tire wear looks manageable"

    if latest["tire_age"] >= 15:
        recommendation = "pit_now"
        reason = "tire age is high"
    if latest_weather.get("rain_probability", 0) >= 0.4:
        recommendation = "prepare_intermediate_window"
        reason = "rain risk is increasing"

    return {
        "driver_id": driver_id,
        "lap": latest["lap"],
        "current_tire_compound": latest["tire_compound"],
        "current_tire_age": latest["tire_age"],
        "weather_rain_probability": latest_weather.get("rain_probability"),
        "recommendation": recommendation,
        "reason": reason,
    }

app = mcp.streamable_http_app()
