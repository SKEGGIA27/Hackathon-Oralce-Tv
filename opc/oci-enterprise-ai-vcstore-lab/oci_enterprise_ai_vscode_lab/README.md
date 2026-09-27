# Hands-on Lab: OCI Enterprise AI Response API in Visual Studio Code

Questo laboratorio guida l'esecuzione di un piccolo flusso Python su OCI Enterprise AI usando Visual Studio Code collegato a una VM OCI.

Il percorso parte da una chiamata semplice alle Response API, prosegue con il caricamento di un documento in un vector store e termina con una chatbot Streamlit che interroga il documento tramite `file_search`.

---

# 1. Obiettivo del laboratorio

Al termine del laboratorio ogni gruppo avra eseguito tre passaggi principali:

1. testare una prima chiamata di inference alle Response API OCI OpenAI-compatible;
2. caricare un file dalla VM e associarlo a un vector store;
3. interrogare il vector store da una chatbot Streamlit.

Tutto il lavoro viene svolto dentro Visual Studio Code collegato alla VM OCI.

---

# 2. Prerequisiti

Sono necessari:

- accesso alla VM OCI assegnata al gruppo;
- Visual Studio Code con connessione remota alla VM;
- Python disponibile sulla VM;
- valori assegnati al gruppo:
  - API key;
  - project id;
  - vector store id.

Le librerie Python necessarie sono elencate nel file `requirements.txt`.

---

# 3. Aprire il progetto in VS Code

Aprire Visual Studio Code e collegarsi alla VM tramite Remote SSH.

Nel terminale integrato di VS Code, entrare nella cartella del laboratorio:

```bash
cd <CARTELLA_DEL_LAB>
```

Tutti i comandi successivi devono essere eseguiti nel terminale integrato di VS Code, dentro la sessione remota della VM.

---

# 4. Struttura del progetto

La cartella contiene questi file:

```text
oci_enterprise_ai_vscode_lab/
├── .env
├── 01_simple_response.py
├── 02_upload_file_to_vector_store.py
├── 03_file_search_server.py
├── 04_streamlit_chatbot.py
├── requirements.txt
└── README.md
```

I file sono numerati nell'ordine di esecuzione.

---

# 5. Configurare il file .env

Aprire il file `.env` in VS Code e sostituire i placeholder con i valori assegnati al gruppo.

```bash
OCI_GENAI_API_KEY="<INSERIRE_API_KEY_DEL_GRUPPO>"
OCI_GENAI_PROJECT_ID="<INSERIRE_PROJECT_ID_DEL_GRUPPO>"
OCI_VECTOR_STORE_ID="<INSERIRE_VECTOR_STORE_ID_DEL_GRUPPO>"
OCI_GENAI_BASE_URL="https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com/openai/v1"
OCI_GENAI_MODEL="openai.gpt-oss-120b"
OCI_FILE_PATH="are_emergent_abilitis_a_mirage.pdf"
FILE_SEARCH_SERVER_URL="http://127.0.0.1:8000"
```

Il file `.env` viene letto automaticamente dagli script Python. Dopo ogni modifica al file `.env`, riavviare gli script in esecuzione.

---

# 6. Creare il virtual environment Python

Visual Studio Code non crea sempre automaticamente il virtual environment Python.

Per questo laboratorio e consigliato crearlo esplicitamente dal terminale integrato di VS Code:

```bash
python3.12 -m venv .venv
```

Attivare il virtual environment:

```bash
source .venv/bin/activate
```

Quando il virtual environment e attivo, il terminale mostra di solito il prefisso:

```text
(.venv)
```

Se VS Code chiede quale interprete Python usare, selezionare quello nella cartella:

```text
.venv/bin/python
```

In alternativa, aprire la Command Palette:

```text
Cmd/Ctrl + Shift + P
```

Eseguire:

```text
Python: Select Interpreter
```

e scegliere l'interprete `.venv`.

---

# 7. Installare le dipendenze Python

Dal terminale integrato di VS Code:

```bash
pip install -r requirements.txt
```

Le dipendenze vengono installate nel virtual environment attivo.

---

# 8. Esercizio 1: testare le Response API

Il primo esercizio verifica che la VM riesca a chiamare le Response API OCI OpenAI-compatible.

Aprire il file:

```text
01_simple_response.py
```

Eseguire:

```bash
python 01_simple_response.py
```

Risultato atteso:

```text
4
```

Questo conferma che API key, project id, endpoint e modello sono configurati correttamente.

---

# 9. Esercizio 2: caricare un file nel vector store

Il secondo esercizio carica un documento locale su OCI e lo associa al vector store.

Prima di eseguire lo script, verificare che il file indicato in `.env` esista nella cartella del laboratorio:

```bash
ls -l are_emergent_abilitis_a_mirage.pdf
```

Se il file ha un nome diverso, aggiornare questa riga nel file `.env`:

```bash
OCI_FILE_PATH="<NOME_DEL_FILE_PDF>"
```

Eseguire:

```bash
python 02_upload_file_to_vector_store.py
```

Risultato atteso:

```text
File creato: <file_id>
Vector store file creato: <vector_store_file_id>
Status iniziale: <status>
```

Il file viene caricato e collegato al vector store indicato da `OCI_VECTOR_STORE_ID`.

---

# 10. Esercizio 3: avviare il server file_search

Il terzo esercizio espone una piccola API locale che riceve una domanda e interroga il vector store tramite `file_search`.

Nel terminale integrato di VS Code, eseguire:

```bash
python 03_file_search_server.py
```

Il server resta in esecuzione sulla porta `8000`.

Lasciare aperto questo terminale.

---

# 11. Esercizio 4: avviare la chatbot Streamlit

Aprire un secondo terminale integrato in VS Code:

```text
Terminal > New Terminal
```

Entrare nella stessa cartella del laboratorio ed eseguire:

```bash
streamlit run 04_streamlit_chatbot.py
```

Streamlit mostrera un URL da aprire nel browser.

Nella chat, scrivere una domanda sul documento caricato nel vector store.

Esempio:

```text
Che cosa sono le emergent abilities nei Large Language Models?
```

La domanda viene inviata al server FastAPI, che chiama le Response API OCI usando `file_search`.

---

# 12. Flusso applicativo

```text
Utente
  |
  v
Chatbot Streamlit
  |
  v
Server FastAPI locale
  |
  v
Response API OCI OpenAI-compatible
  |
  v
Vector store + file_search
  |
  v
Risposta generata
```

---

# 13. Troubleshooting

## KeyError su una variabile

Esempio:

```text
KeyError: 'OCI_GENAI_API_KEY'
```

Significa che la variabile non e presente nel file `.env` oppure il file `.env` non si trova nella stessa cartella dello script.

## No VectorStore found

Verificare che `OCI_VECTOR_STORE_ID` sia completo e appartenga allo stesso project configurato in `OCI_GENAI_PROJECT_ID`.

## Streamlit mostra errore di connessione

Verificare che il server sia in esecuzione:

```bash
python 03_file_search_server.py
```

Verificare anche che nel file `.env` sia presente:

```bash
FILE_SEARCH_SERVER_URL="http://127.0.0.1:8000"
```

## Il file PDF non viene trovato

Verificare il nome del file:

```bash
ls -l
```

Poi aggiornare `OCI_FILE_PATH` nel file `.env`.

---

# 14. Workflow consigliato in VS Code

1. Aprire VS Code collegato alla VM.
2. Aprire la cartella del laboratorio.
3. Configurare `.env`.
4. Creare e attivare il virtual environment `.venv`.
5. Installare le dipendenze.
6. Eseguire `01_simple_response.py`.
7. Eseguire `02_upload_file_to_vector_store.py`.
8. Avviare `03_file_search_server.py`.
9. In un secondo terminale avviare `04_streamlit_chatbot.py`.
10. Scrivere la domanda nella chat.

---

# 15. Note finali

Questo laboratorio introduce un flusso Retrieval-Augmented Generation su OCI Enterprise AI.

Il modello non risponde solo sulla base del prompt, ma puo recuperare contenuto dal documento indicizzato nel vector store tramite `file_search`.
