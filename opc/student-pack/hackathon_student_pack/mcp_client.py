import os
from pathlib import Path
import json         
import requests

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI


# Legge le variabili dal file .env presente nella stessa cartella.
load_dotenv(Path(__file__).with_name(".env"), override=True)

# Configurazione OCI Enterprise AI letta dal file .env.
BASE_URL = os.environ["OCI_GENAI_BASE_URL"]
API_KEY = os.environ["OCI_GENAI_API_KEY"]
PROJECT_ID = os.environ["OCI_GENAI_PROJECT_ID"]
VECTOR_STORE_ID = os.environ["OCI_VECTOR_STORE_ID"]
MODEL = os.environ["OCI_GENAI_MODEL"]

# Client OpenAI-compatible verso OCI Generative AI.
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    project=PROJECT_ID,
)

# Applicazione FastAPI.
app = FastAPI()


@app.post("/query")
def query_vector_store(request: dict):
    # La chatbot invia un JSON di questo tipo:
    # {"query": "domanda scritta dall'utente"}
    user_query = request["query"]

    response = client.responses.create(
        model=MODEL,
        instructions="""Answer using only information from the retrieved documents.
You may summarize or synthesize information that is explicitly supported by the retrieved text.
Do not use outside knowledge.
If the answer is not contained in the documents, say: "I don't know."
""",
        input=user_query,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [VECTOR_STORE_ID],
            }
        ],
    )

    return {"answer": response.output_text}


TELEMETRY_SERVER_URL = "http://127.0.0.1:8100"

def get_telemetry_tools_for_llm():
    try:
        response = requests.get(f"{TELEMETRY_SERVER_URL}/tools")
        server_tools = response.json()["tools"]
        
        openai_tools = []
        for t in server_tools:
            properties = {}
            required = []
            for param_name, param_info in t["parameters"].items():
                properties[param_name] = {
                    "type": param_info["type"],
                    "description": param_info.get("description", "")
                }
                if param_info.get("required"):
                    required.append(param_name)
                    
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": {"type": "object", "properties": properties, "required": required}
                }
            })
        return openai_tools
    except Exception as e:
        print(f"Errore connessione server telemetria: {e}")
        return []

def esegui_tool_telemetria(nome_tool: str, argomenti: dict) -> str:
    try:
        response = requests.get(f"{TELEMETRY_SERVER_URL}/tools/{nome_tool}", params=argomenti)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Errore dal server telemetrico: {str(e)}"})

@app.post("/query_telemetria")
def query_mcp_telemetry(request: dict):
    user_query = request["query"]
    tools = get_telemetry_tools_for_llm()

    messages = [
        {"role": "system", "content": "Sei l'AI Race Engineer del team. Usa gli strumenti telemetrici a tua disposizione per rispondere allo stato della vettura. Rispondi SEMPRE in italiano con un'analisi dettagliata."},
        {"role": "user", "content": user_query}
    ]

    if not tools:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        answer = response.choices[0].message.content
        return {"answer": answer or "Nessuno strumento telemetrico disponibile. Riprova più tardi."}

    # Multi-turn tool call loop (max 5 rounds to avoid infinite loops)
    MAX_TOOL_ROUNDS = 5
    for round_num in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        messaggio_ai = response.choices[0].message

        if not messaggio_ai.tool_calls:
            # No more tool calls — we have a final text response
            if messaggio_ai.content:
                return {"answer": messaggio_ai.content}
            break  # content is None, fall through to fallback

        # Process tool calls
        messages.append(messaggio_ai)
        for tool_call in messaggio_ai.tool_calls:
            nome_tool = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"[Telemetria] Round {round_num+1}: tool={nome_tool}, args={args}")
            dati_telemetria = esegui_tool_telemetria(nome_tool, args)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": dati_telemetria})

    # If we exited the loop without a text response, do a final call without tools
    # to force the model to produce a text answer from the data it already collected
    print("[Telemetria] Forcing final text response without tools...")
    try:
        # Build a clean messages list: keep system + user + any tool results as context
        final_messages = [m for m in messages if m.get("role") in ("system", "user", "tool") or (isinstance(m, dict) and m.get("role") == "assistant" and m.get("content"))]
        # If that filtered too aggressively, just use original messages
        if len(final_messages) < 2:
            final_messages = messages
        risposta_finale = client.chat.completions.create(model=MODEL, messages=messages)
        answer = risposta_finale.choices[0].message.content
        if answer:
            return {"answer": answer}
    except Exception as e:
        print(f"[Telemetria] Fallback error: {e}")

    return {"answer": "Non sono riuscito a generare una risposta completa. Prova a riformulare la domanda in modo più specifico."}


# ---------------------------------------------------------------------------
# Endpoint dashboard-aware: restituisce answer + chart_config JSON
# ---------------------------------------------------------------------------

DASHBOARD_SYSTEM_PROMPT = """\
Sei l'AI Race Engineer del team. Usa gli strumenti telemetrici a tua disposizione per rispondere.

IMPORTANTE: devi SEMPRE restituire la tua risposta come un singolo blocco JSON valido (senza ```json, senza markdown) con questa struttura esatta:

{
  "answer": "La tua risposta testuale qui...",
  "chart_config": {
    "start_lap": <primo lap da visualizzare, intero>,
    "end_lap": <ultimo lap da visualizzare, intero>,
    "categories": ["<lista delle categorie attive, es: gomme, energia, freni, posizione>"],
    "fields": ["<campo telemetrico da visualizzare>"],
    "metrics": [
      {"type": "<average|max|min>", "field": "<campo>", "label": "<etichetta>"}
    ],
    "chart_type": "<line|bar|area>"
  }
}

Regole per chart_config:
- "categories" è una LISTA di categorie. Usa le chip attive indicate nel messaggio utente. Valori possibili: "gomme" (pneumatici: usura, temperatura, pressione), "energia" (batteria/SoC/ERS), "freni" (temperature freni), "posizione" (posizione in gara e tempi sul giro). Se l'utente ha più chip attive, includi TUTTE nella lista.
- "start_lap" e "end_lap" definiscono l'intervallo di giri. Si applicano a TUTTE le categorie nella lista. Se l'utente non specifica un intervallo, usa start_lap=1 e end_lap=50.
- "fields" usa i nomi dei campi telemetrici: "tires.temperature_c", "tires.wear_pct", "tires.pressure_bar", "energy_system", "brake_temperatures_c", "position", "lap_time_s".
- "metrics" specifica i calcoli da mostrare: type può essere "average", "max", o "min".
- Se non riesci a generare un chart_config valido, restituisci chart_config come null e spiega il problema nel campo answer.

Rispondi SOLO con il JSON, senza altro testo prima o dopo.
"""


@app.post("/query_telemetria_dashboard")
def query_mcp_telemetry_dashboard(request: dict):
    user_query = request["query"]
    active_chips = request.get("active_chips", [])
    tools = get_telemetry_tools_for_llm()

    # Aggiungi contesto delle chip attive al prompt utente
    chip_context = ""
    if active_chips:
        chip_context = f" [Chip attive: {', '.join(active_chips)}]"

    messages = [
        {"role": "system", "content": DASHBOARD_SYSTEM_PROMPT},
        {"role": "user", "content": user_query + chip_context}
    ]

    if not tools:
        response = client.chat.completions.create(model=MODEL, messages=messages)
        raw = response.choices[0].message.content
        return _parse_dashboard_response(raw)

    response = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    messaggio_ai = response.choices[0].message

    if messaggio_ai.tool_calls:
        messages.append(messaggio_ai)

        for tool_call in messaggio_ai.tool_calls:
            nome_tool = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            dati_telemetria = esegui_tool_telemetria(nome_tool, args)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": dati_telemetria})

        risposta_finale = client.chat.completions.create(model=MODEL, messages=messages)
        raw = risposta_finale.choices[0].message.content
        return _parse_dashboard_response(raw)

    return _parse_dashboard_response(messaggio_ai.content)


def _parse_dashboard_response(raw_text: str) -> dict:
    """Parse the AI response, extracting JSON with answer + chart_config."""
    if not raw_text:
        return {
            "answer": "⚠️ Non sono riuscito a generare una risposta valida. Mostro la dashboard di default.",
            "chart_config": None
        }

    # Prova a parsare direttamente come JSON
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict) and "answer" in parsed:
            return {
                "answer": parsed.get("answer", ""),
                "chart_config": parsed.get("chart_config", None)
            }
    except json.JSONDecodeError:
        pass

    # Prova a estrarre JSON da eventuale markdown ```json ... ```
    import re
    json_match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict) and "answer" in parsed:
                return {
                    "answer": parsed.get("answer", ""),
                    "chart_config": parsed.get("chart_config", None)
                }
        except json.JSONDecodeError:
            pass

    # Prova a trovare un blocco JSON generico nel testo
    json_match = re.search(r'\{[\s\S]*"answer"[\s\S]*\}', raw_text)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            return {
                "answer": parsed.get("answer", raw_text),
                "chart_config": parsed.get("chart_config", None)
            }
        except json.JSONDecodeError:
            pass

    # Fallback: restituisci il testo grezzo come answer senza chart_config
    return {
        "answer": raw_text + "\n\n⚠️ _Non sono riuscito a generare un chart_config valido. Dashboard di default._",
        "chart_config": None
    }


if __name__ == "__main__":
    import uvicorn
 
    uvicorn.run(app, host="0.0.0.0", port=8000)