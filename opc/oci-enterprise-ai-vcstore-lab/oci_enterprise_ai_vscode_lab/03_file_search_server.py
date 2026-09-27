import os
from pathlib import Path

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
