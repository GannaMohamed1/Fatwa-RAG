import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────
# Groq
# ─────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODEL = "llama-3.1-8b-instant"

# ─────────────────────────────────────────────────────────────
# Embeddings
# ─────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "BAAI/bge-m3"

EMBEDDING_DEVICE = "cpu"
# ─────────────────────────────────────────────────────────────
# Retrieval
# ─────────────────────────────────────────────────────────────

TOP_K_RETRIEVAL = 10


TOP_K_FINAL = 3


DENSE_WEIGHT = 0.75

BM25_WEIGHT = 0.25

MIN_CONFIDENCE = 0.45

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────

INDEX_DIR = "indexes"

FAISS_INDEX = os.path.join(
    INDEX_DIR,
    "faiss.index"
)

BM25_PATH = os.path.join(
    INDEX_DIR,
    "bm25.pkl"
)

METADATA_PATH = os.path.join(
    INDEX_DIR,
    "metadata.pkl"
)

DATA_PATH = os.path.join(
    "data",
    "qa_data.xlsx"
)

QUESTION_COL = "Question"

ANSWER_COL = "Answer"

# ─────────────────────────────────────────────────────────────
# Server
# ─────────────────────────────────────────────────────────────

BACKEND_HOST = "0.0.0.0"

BACKEND_PORT = 8000

FRONTEND_PORT = 7860

# ─────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────

ALLOWED_ORIGINS = [
    "*"
]