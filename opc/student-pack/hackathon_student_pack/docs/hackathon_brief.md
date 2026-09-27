# Hackathon Brief: AI Race Engineer Challenge

## 1. Narrative

Scuderia Tor Vergata is running a full endurance simulation before a high-visibility test event. Engineers must monitor live race telemetry, evaluate whether newly designed components can legally be fitted to the car, and provide decision support through an AI race engineer copilot that can speak clearly to technical and non-technical users.

The three tasks are connected on purpose. Task 1 creates the live telemetry foundation. Task 2 creates the regulation and component-reasoning foundation. Task 3 turns both back-end systems into a coherent product that feels like a real team tool instead of a classroom prototype.

## 2. Learning Goals

- Build AI systems that work with structured telemetry, live updates, and tool-calling.
- Design an MCP server that gives language models controlled access to engineering data.
- Apply anomaly detection and explainable strategy reasoning to motorsport problems.
- Build a practical RAG system that cites regulation clauses instead of guessing.
- Deliver a conversational product that merges operations, compliance, and communication.

## 3. Task 1: Telemetry Intelligence Platform With MCP Server

Students receive a lap-by-lap telemetry dataset for a 50-lap endurance session. The dataset includes tyre temperatures, tyre wear, lap and sector times, brake temperatures, battery energy, ERS deployment, weather, track grip evolution, tyre pressures, pit events, race-control phases, and nearby race context.

### Required outputs

- An MCP server that exposes structured telemetry access to AI clients.
- An AI telemetry analyst that accepts natural-language questions and calls MCP tools when needed.
- An anomaly-detection workflow for tyre, brake, energy, or pace issues.
- Strategy logic that can recommend pit timing and estimate race impact.

### Minimum capabilities

- Query by lap, stint, component, track condition, and race status.
- Retrieve current and historical views of tyre, brake, energy, and pace data.
- Replay the JSONL stream to simulate real-time telemetry.
- Compare observed tyre wear with the provided expected wear model.
- Explain why the model recommends or rejects a strategy change.

### Mandatory scenario

The front-left tyre begins degrading abnormally from lap 17 onward after a brief lock-up and high track temperatures. By lap 23 the deviation to the baseline wear model reaches about 18 percentage points with 27 laps remaining. Good solutions should infer that the tyre will fall out of its effective operating window within about six laps and should recommend a stop between laps 24 and 26.

## 4. Task 2: Regulatory Compliance RAG System

Students ingest the regulation handbook and the technical dossier into a searchable knowledge base. The goal is not only to retrieve relevant passages, but to answer engineering questions with traceable reasoning.

### Required outputs

- Document ingestion pipeline for the rulebook and component dossier.
- Chunking and vector indexing strategy suited to long technical documents.
- Semantic search or hybrid retrieval for regulation questions.
- An answer engine that explains compliance decisions and cites the right sections.

### Example challenge questions

1. Is the new rear wing geometry compliant with aerodynamic regulations?
2. Can the BAT-X9 accumulator enclosure material be used under the safety rules?
3. Does the SA-LF-OPT suspension arm satisfy the dimensional constraints?

### What strong solutions do

- Distinguish between directly compliant, non-compliant, and insufficient-information cases.
- Cite sections precisely instead of making vague claims.
- Explain the reason for the verdict in engineering language.
- Compare component dimensions or materials against explicit numeric limits.

## 5. Task 3: AI Race Engineer Conversational Application

Students build a web application that combines Task 1 and Task 2 into one assistant. The product should feel like a digital race engineer that can support the strategy desk, design office, and media lead in the same environment.

### Required user flows

- Ask telemetry and strategy questions in plain language.
- Inspect tyre degradation and pace trends through simple visualizations.
- Query rule compliance and receive quoted regulation support.
- Ask about new experimental parts in the technical dossier.
- Generate public-facing race updates or celebratory social media copy.

### Example media request

Generate an exciting social media post after a successful tyre strategy during the final laps.

### Example answer style

What a comeback by Scuderia Tor Vergata!
An aggressive but data-backed tyre call turned the race around in the closing phase. Fresh hard tyres, disciplined energy deployment, and clean overtakes brought the car back into the top five. Data-driven racing at its finest. #Motorsport #AI #RaceStrategy

## 6. Suggested Architecture

- Telemetry data source: JSON plus JSONL replay for live simulation.
- MCP layer: tool endpoints for session summary, lap windows, component history, wear-model comparison, and strategy context.
- Telemetry agent: reasoning loop with anomaly detection, forecasts, and natural-language reporting.
- RAG layer: embeddings, vector store, citation-aware answer generation.
- Web app: one chat surface with tabs or panels for telemetry, compliance, and media outputs.

## 7. Student Deliverables

1. Source code for the MCP server, retrieval system, and conversational app.
2. A working demo that answers at least one telemetry question, one compliance question, and one media-generation prompt.
3. Short technical documentation explaining architecture choices and limitations.
4. A demonstration of how the assistant responds to the front-left tyre anomaly scenario.

## 8. Suggested Judging Criteria

1. Engineering usefulness: Are the outputs helpful to a racing team under time pressure?
2. Technical quality: Are MCP integration, retrieval, and tool usage reliable?
3. Explainability: Does the system justify recommendations clearly and cite evidence?
4. Product design: Is the conversational experience fast, intuitive, and well structured?
5. Realism: Do answers respect race conditions, tyre behaviour, and regulation language?

## 9. Stretch Goals

- Multi-agent orchestration between strategist, compliance engineer, and media assistant roles.
- Probabilistic position-loss forecasting based on competitor gaps.
- Incident summaries after yellow-flag or safety-car events.
- Voice interface for pit-wall style interactions.
- Automatic generation of end-of-session engineering reports.

## 10. Organizer Notes

This package is intentionally opinionated. The telemetry anomaly is strong enough to be detectable, but not so obvious that students can solve it with a single threshold rule. The regulation set contains both compliant and non-compliant experimental parts so the RAG system has to reason carefully. The final application should reward teams that blend tool use, retrieval, and product thinking into one polished workflow.
