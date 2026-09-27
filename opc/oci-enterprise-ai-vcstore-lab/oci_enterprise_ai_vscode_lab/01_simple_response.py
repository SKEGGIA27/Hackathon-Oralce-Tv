import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Legge le variabili dal file .env presente nella stessa cartella.
load_dotenv(Path(__file__).with_name(".env"), override=True)

# Configurazione OCI Enterprise AI letta dal file .env.
BASE_URL = os.environ["OCI_GENAI_BASE_URL"]
API_KEY = os.environ["OCI_GENAI_API_KEY"]
PROJECT_ID = os.environ["OCI_GENAI_PROJECT_ID"]
MODEL = os.environ["OCI_GENAI_MODEL"]

# Client OpenAI-compatible verso OCI Generative AI.
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    project=PROJECT_ID,
)

# Prima chiamata semplice alle Response API.
response = client.responses.create(
    model=MODEL,
    input="What is 2x2?",
)

print(response.output_text)
