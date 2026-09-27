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
VECTOR_STORE_ID = os.environ["OCI_VECTOR_STORE_ID"]
FILE_PATH = os.environ["OCI_FILE_PATH"]
FILE_PATH2 = os.environ["OCI_FILE_PATH2"]

# Client OpenAI-compatible verso OCI Generative AI.
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    project=PROJECT_ID,
)

# Upload del file locale verso OCI.
with open(FILE_PATH, "rb") as file:
    uploaded_file = client.files.create(
        file=file,
        purpose="user_data",
    )

print("File creato:", uploaded_file.id)

# Associazione del file al vector store.
vector_store_file = client.vector_stores.files.create(
    vector_store_id=VECTOR_STORE_ID,
    file_id=uploaded_file.id,
    attributes={
        "source": "local_upload",
        "topic": "hackathon",
    },
)

print("Vector store file creato:", vector_store_file.id)
print("Status iniziale:", vector_store_file.status)


# Upload del file locale verso OCI.
with open(FILE_PATH2, "rb") as file:
    uploaded_file2 = client.files.create(
        file=file,
        purpose="user_data",
    )

print("File creato:", uploaded_file2.id)

# Associazione del file al vector store.
vector_store_file2 = client.vector_stores.files.create(
    vector_store_id=VECTOR_STORE_ID,
    file_id=uploaded_file2.id,
    attributes={
        "source": "local_upload",
        "topic": "hackathon",
    },
)

print("Vector store file creato:", vector_store_file2.id)
print("Status iniziale:", vector_store_file2.status)
