import os
from pathlib import Path

from dotenv import load_dotenv
import requests
import streamlit as st


# Legge l'indirizzo del server FastAPI dal file .env.
load_dotenv(Path(__file__).with_name(".env"), override=True)
SERVER_URL = os.environ["FILE_SEARCH_SERVER_URL"].rstrip("/")


def call_server(query: str) -> str:
    # Invia al server la domanda scritta dall'utente.
    response = requests.post(
        f"{SERVER_URL}/query",
        json={"query": query},
        timeout=120,
    )

    # Il server risponde con un JSON di questo tipo:
    # {"answer": "risposta generata dal modello"}
    return response.json()["answer"]


st.set_page_config(page_title="OCI File Search Chatbot")
st.title("OCI Enterprise AI File Search")

# Lista dei messaggi mostrati nella chat.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Scrivi una domanda sul documento caricato nel vector store.",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo in cui l'utente scrive la domanda.
prompt = st.chat_input("Scrivi la tua domanda")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = call_server(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
