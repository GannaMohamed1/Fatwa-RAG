# Fatwa RAG System

Arabic Retrieval-Augmented Generation system for Islamic Q&A with:

- hybrid retrieval: FAISS + BM25
- Arabic normalization and topic inference
- Groq-powered query rewriting and answer generation
- professional Arabic frontend
- suggested questions loaded from your Excel data
- feedback logging
- related fatwas display

## What it uses

The language layer is configured to use Groq's OpenAI-compatible API, and the default model is `llama-3.1-8b-instant`. Groq documents this model as low-latency and suitable for real-time interfaces, and Groq's API is OpenAI-compatible through `https://api.groq.com/openai/v1`.  

## Setup

### 1) Create a virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 2) Install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Add your Groq key
Copy `.env.example` to `.env` and set:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4) Put your dataset in place
The project expects:

```text
data/qa_data.xlsx
```

with columns:

- `Question`
- `Answer`

### 5) Build the index
```powershell
python scripts/build_index.py
```

### 6) Start everything
```powershell
python run.py
```

Open:

- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:7860`

## Run components separately

Backend:
```powershell
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

Frontend:
```powershell
python frontend/frontend.py
```

## Project files

- `api/app.py` — FastAPI backend
- `src/data_loader.py` — load and clean dataset
- `src/embeddings.py` — dense embeddings
- `src/retrieval.py` — FAISS + BM25 retrieval
- `src/groq_client.py` — Groq Arabic helper
- `src/generator.py` — answer formatting
- `src/pipeline.py` — orchestration
- `frontend/frontend.py` — professional Arabic UI
- `scripts/build_index.py` — index builder
- `scripts/query_api.py` — quick API test
- `scripts/test_pipeline.py` — CLI test tool
- `run.py` — launch backend + frontend

## Notes

- The system is optimized for Arabic and uses a strict answer style.
- If Groq is unavailable, the backend falls back to extractive answers from the retrieved fatwas.
- Feedback submitted from the frontend is stored in `data/feedback.jsonl`.
