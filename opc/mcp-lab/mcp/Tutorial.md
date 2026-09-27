# F1 Race Strategy Assistant with MCP and OCI Enterprise AI

## Overview

This tutorial demonstrates how to build and deploy a simple MCP (Model Context Protocol) server on an OCI Compute Instance and connect it to OCI Enterprise AI using the OCI Enterprise AI Responses API — OpenAI Compatible endpoint.

The solution combines:

* OCI Compute Instance hosting the MCP server
* OCI Enterprise AI Responses API
* OpenAI-compatible Python SDK
* MCP (Model Context Protocol)
* simulated Formula 1 race telemetry data

The use case simulates a Formula 1 race assistant capable of:

* summarizing a race session
* retrieving driver positions
* comparing driver performance
* recommending pit strategies

---

# What is MCP?

MCP (Model Context Protocol) is an open protocol that allows AI models to interact with external tools and data sources in a standardized way.

Instead of hardcoding APIs directly into the application, MCP exposes capabilities as reusable tools that models can dynamically discover and invoke.

An MCP server can expose:

* databases
* REST APIs
* files
* analytics systems
* monitoring systems
* custom Python functions

The AI model can then:

1. discover available tools
2. decide which tool to call
3. execute the tool
4. use the returned data to generate a final response

In this tutorial:

* the MCP server exposes F1 race analysis tools
* OCI Enterprise AI imports those tools dynamically
* the model uses them to answer racing questions

---

# Architecture

```text
OCI Enterprise AI Responses API
(OpenAI Compatible)
        |
        |  Responses API + MCP
        |
        v
Remote MCP Server on OCI VM
        |
        v
Local JSON Race Data
```

This implementation uses the OCI Enterprise AI OpenAI-compatible endpoint, allowing developers to reuse the standard OpenAI Python SDK while running inference on OCI-hosted models.

---

# Learning Objectives

By the end of this tutorial, students will be able to:

* understand the basics of MCP
* create an MCP server using Python
* expose Python functions as MCP tools
* deploy an MCP server on OCI Compute
* connect OCI Enterprise AI to an MCP server
* use the OpenAI-compatible OCI endpoint
* invoke MCP tools dynamically from a model

---

# Prerequisites

Students should have:

* basic Python knowledge
* an OCI account
* an OCI Compute Instance with public IP
* OCI Enterprise AI access
* Python 3.10+

---

# Project Structure

```text
mcp/
├── data/
│   ├── lap_times.json
│   ├── race_events.json
│   ├── session_metadata.json
│   └── weather.json
├── mcp_server.py
├── mcp_client.py
└── requirements.txt
```

---

# Install Dependencies

Create a virtual environment:

```bash
python3.12 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install openai mcp uvicorn
```

---

# Configure Environment Variables

Set the OCI Enterprise AI and MCP configuration variables.

```bash
export OCI_OPENAI_BASE_URL="https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com/openai/v1"

export OCI_GENAI_API_KEY="<your-api-key>"

export OCI_GENAI_PROJECT_OCID="<your-project-ocid>"

export OCI_MODEL_ID="openai.gpt-oss-120b"

export F1_MCP_SERVER_URL="http://<public-ip>:8000/mcp"
```

Example:

```bash
export F1_MCP_SERVER_URL="http://204.216.211.102:8000/mcp"
```

---

# Understanding the Data

The MCP server reads race information from local JSON files.

## session_metadata.json

Contains general session information:

```json
{
  "session_id": "monza_gp",
  "season": 2025,
  "circuit": "Monza",
  "session_type": "Race",
  "laps": 53
}
```

---

## lap_times.json

Contains telemetry per lap:

```json
[
  {
    "driver_id": "NOR",
    "lap": 12,
    "position": 2,
    "lap_time_ms": 82345,
    "gap_to_leader_ms": 1450,
    "tire_compound": "MEDIUM",
    "tire_age": 10
  }
]
```

---

## weather.json

Contains weather information:

```json
[
  {
    "lap": 30,
    "rain_probability": 0.45
  }
]
```

---

# Step 1 — Create the MCP Server

Create a file called `mcp_server.py`.

## MCP Server Code

```python
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# FastMCP allows Python functions to be exposed as MCP tools
from mcp.server.fastmcp import FastMCP

# Transport security configuration
from mcp.server.transport_security import TransportSecuritySettings


# Directory containing local JSON data
DATA_DIR = Path(__file__).parent / "data"


# Create MCP server
mcp = FastMCP(
    "F1 Hackathon Server",

    # Stateless mode simplifies HTTP integrations
    stateless_http=True,

    # Return JSON responses
    json_response=True,

    # Disable DNS rebinding protection for lab/demo usage
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# Helper function to load JSON files
def _load_json(name: str) -> Any:

    path = DATA_DIR / name

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Load lap telemetry
def _latest_laps() -> List[Dict[str, Any]]:
    return _load_json("lap_times.json")


# ---------------------------------------------------------
# MCP TOOL: SESSION OVERVIEW
# ---------------------------------------------------------
@mcp.tool()
def get_session_overview() -> Dict[str, Any]:
    """
    Return high-level race session information.
    """

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


# ---------------------------------------------------------
# MCP TOOL: DRIVER POSITION
# ---------------------------------------------------------
@mcp.tool()
def get_driver_position(
    driver_id: str,
    lap: Optional[int] = None
) -> Dict[str, Any]:
    """
    Return driver race position information.
    """

    laps = _latest_laps()

    driver_laps = [
        row for row in laps
        if row["driver_id"] == driver_id
    ]

    if not driver_laps:
        return {
            "driver_id": driver_id,
            "found": False
        }

    # Return latest lap if lap number not provided
    if lap is None:
        row = max(driver_laps, key=lambda x: x["lap"])

    else:
        matches = [
            row for row in driver_laps
            if row["lap"] == lap
        ]

        if not matches:
            return {
                "driver_id": driver_id,
                "lap": lap,
                "found": False
            }

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


# ---------------------------------------------------------
# MCP TOOL: DRIVER COMPARISON
# ---------------------------------------------------------
@mcp.tool()
def compare_drivers(
    driver_a: str,
    driver_b: str,
    lap_start: int,
    lap_end: int
) -> Dict[str, Any]:
    """
    Compare average lap time between two drivers.
    """

    laps = _latest_laps()

    def avg_lap_time(driver_id: str):

        rows = [
            row["lap_time_ms"]
            for row in laps
            if (
                row["driver_id"] == driver_id
                and lap_start <= row["lap"] <= lap_end
            )
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
        "faster_driver": (
            driver_a if a and b and a < b
            else driver_b if a and b and b < a
            else None
        ),
    }


# ---------------------------------------------------------
# MCP TOOL: STRATEGY RECOMMENDATION
# ---------------------------------------------------------
@mcp.tool()
def recommend_strategy(driver_id: str) -> Dict[str, Any]:
    """
    Recommend a pit strategy using tire wear and weather.
    """

    laps = _latest_laps()
    weather = _load_json("weather.json")

    driver_rows = [
        row for row in laps
        if row["driver_id"] == driver_id
    ]

    if not driver_rows:
        return {
            "driver_id": driver_id,
            "found": False
        }

    latest = max(driver_rows, key=lambda x: x["lap"])
    latest_weather = max(weather, key=lambda x: x["lap"])

    recommendation = "stay_out"
    reason = "tire wear looks manageable"

    # Tire degradation logic
    if latest["tire_age"] >= 15:
        recommendation = "pit_now"
        reason = "tire age is high"

    # Rain strategy logic
    if latest_weather.get("rain_probability", 0) >= 0.4:
        recommendation = "prepare_intermediate_window"
        reason = "rain risk is increasing"

    return {
        "driver_id": driver_id,
        "lap": latest["lap"],
        "current_tire_compound": latest["tire_compound"],
        "current_tire_age": latest["tire_age"],
        "weather_rain_probability":
            latest_weather.get("rain_probability"),
        "recommendation": recommendation,
        "reason": reason,
    }


# Create ASGI app
app = mcp.streamable_http_app()


# Local execution entry point
if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
```

---

# Step 2 — Start the MCP Server

Run the server:

```bash
uvicorn mcp_server:app --host 0.0.0.0 --port 8000
```

Verify the server is listening:

```bash
ss -ltnp | grep 8000
```

Expected:

```text
0.0.0.0:8000
```

---

# Step 3 — Configure OCI Networking

Ensure the OCI subnet or NSG allows inbound TCP traffic on port 8000.

Example ingress rule:

| Source CIDR | Protocol | Port |
| ----------- | -------- | ---- |
| 0.0.0.0/0   | TCP      | 8000 |

---

# Step 4 — Create the MCP Client

Create a file called `mcp_client.py`.

## MCP Client Code

```python
import os

# OpenAI SDK used with OCI Enterprise AI
from openai import OpenAI


# Create OCI Enterprise AI client
client = OpenAI(

    # OCI OpenAI-compatible endpoint
    base_url=os.environ["OCI_OPENAI_BASE_URL"],

    # OCI API key
    api_key=os.environ["OCI_GENAI_API_KEY"],

    # OCI Generative AI project
    project=os.environ["OCI_GENAI_PROJECT_OCID"],
)


# Send request to OCI Enterprise AI
response = client.responses.create(

    # OCI-hosted model
    model=os.environ["OCI_MODEL_ID"],

    # User prompt
    input=(
        "Use the F1 MCP server to summarize "
        "the race and recommend a pit strategy for NOR."
    ),

    # Register MCP server
    tools=[
        {
            "type": "mcp",

            # Logical MCP server name
            "server_label": "f1_race_server",

            # Description visible to the model
            "server_description": (
                "MCP server exposing simulated "
                "F1 race data and strategy tools"
            ),

            # Public MCP endpoint
            "server_url":
                os.environ["F1_MCP_SERVER_URL"],

            # Automatically allow tool execution
            "require_approval": "never",

            # Restrict accessible MCP tools
            "allowed_tools": [
                "get_session_overview",
                "get_driver_position",
                "compare_drivers",
                "recommend_strategy"
            ],
        }
    ],

    stream=False,
)


# Print final AI response
print(response.output_text)
```

---

# Step 5 — Run the Client

Run:

```bash
python mcp_client.py
```

---

# Example Output

```text
The session is a 53-lap race at Monza.

NOR is currently running P2 with medium tires that are
15 laps old. Rain probability is increasing to 45%.

Recommended strategy:
Prepare for an intermediate tire window because
weather conditions are deteriorating.
```

---

# Troubleshooting

## Server only reachable locally

Check:

```bash
ss -ltnp | grep 8000
```

Bad:

```text
127.0.0.1:8000
```

Good:

```text
0.0.0.0:8000
```

---

## 421 Misdirected Request

Cause:

DNS rebinding protection.

Fix:

```python
transport_security=TransportSecuritySettings(
    enable_dns_rebinding_protection=False
)
```

---

## 424 Failed Dependency

Cause:

OCI Enterprise AI cannot retrieve the MCP tool list.

Common reasons:

* wrong MCP URL
* wrong protocol (`https` vs `http`)
* blocked OCI firewall
* server not publicly reachable

Correct example:

```bash
export F1_MCP_SERVER_URL="http://public-IP:8000/mcp"
```

---

# Conclusion

In this tutorial, students learned how to:

* create a custom MCP server
* expose Python functions as AI tools
* deploy an MCP server on OCI Compute
* connect OCI Enterprise AI Responses API to the MCP server
* use the OCI OpenAI-compatible SDK interface
* dynamically invoke MCP tools from an AI model

This architecture can be reused for:

* enterprise APIs
* databases
* analytics systems
* monitoring platforms
* DevOps tooling
* financial systems
* IoT telemetry
* operational dashboards

MCP provides a scalable and standardized mechanism for connecting OCI-hosted AI models with external tools and enterprise systems.
