"""FastAPI backend for the Fatwa RAG system."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
from src.pipeline import RAGPipeline


# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s"
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# FastAPI
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Fatwa RAG API",
    description="Arabic Fatwa retrieval system powered by hybrid search + Groq.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Globals
# ─────────────────────────────────────────────────────────────

pipeline: Optional[RAGPipeline] = None

FEEDBACK_PATH = (
    Path("data")
    /
    "feedback.jsonl"
)


# ─────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):

    question: str = Field(
        ...,
        description="User question in Arabic.",
    )


class SourceItem(BaseModel):

    question: str
    answer: str
    score: float


class ChatResponse(BaseModel):

    answer: str
    confidence: float
    sources: list[SourceItem]


class FeedbackRequest(BaseModel):

    question: str
    answer: str
    helpful: bool

    comment: str | None = None


# ─────────────────────────────────────────────────────────────
# Startup
# ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():

    global pipeline

    logger.info(
        "Loading RAG pipeline..."
    )

    pipeline = RAGPipeline()

    try:

        pipeline.load_index()

        logger.info(
            "Index loaded."
        )

    except Exception as exc:

        logger.warning(
            "Index not ready yet: %s",
            exc,
        )


# ─────────────────────────────────────────────────────────────
# Root
# ─────────────────────────────────────────────────────────────

@app.get("/")
def root():

    return {
        "status": "ok",
        "message": "Fatwa RAG API is running.",
        "docs": "/docs",
        "health": "/health",
    }


# ─────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():

    return {
        "status": "ok",
        "pipeline_ready": pipeline is not None,
    }


# ─────────────────────────────────────────────────────────────
# Query
# ─────────────────────────────────────────────────────────────

@app.post(
    "/query",
    response_model=ChatResponse,
)
def query(req: QueryRequest):

    if not pipeline:

        raise HTTPException(
            status_code=503,
            detail="Pipeline not ready."
        )

    if not req.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        result = pipeline.answer(
            req.question
        )

        sources = [
            SourceItem(**s)
            for s in result.sources
        ]

        return ChatResponse(
            answer=result.answer,
            confidence=result.confidence,
            sources=sources,
        )

    except Exception as e:

        logger.exception(
            "Query failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ─────────────────────────────────────────────────────────────
# Suggestions
# ─────────────────────────────────────────────────────────────

@app.get("/suggestions")
def suggestions(limit: int = 12):

    from pandas import read_excel

    try:

        df = read_excel(
            config.DATA_PATH
        )

        q = (
            df[
                config.QUESTION_COL
            ]
            .dropna()
            .astype(str)
            .tolist()
        )

        return {
            "suggestions": q[:limit]
        }

    except Exception as exc:

        return {
            "suggestions": [
                "ما حكم الزكاة؟",
                "ما حكم الربا؟",
                "ما حكم صلاة الجماعة؟",
            ],
            "warning": str(exc),
        }


# ─────────────────────────────────────────────────────────────
# Feedback
# ─────────────────────────────────────────────────────────────

@app.post("/feedback")
def feedback(req: FeedbackRequest):

    FEEDBACK_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    row = {
        "timestamp":
            datetime.utcnow().isoformat()
            + "Z",

        "question": req.question,

        "answer": req.answer,

        "helpful": req.helpful,

        "comment": req.comment,
    }

    with FEEDBACK_PATH.open(
        "a",
        encoding="utf-8",
    ) as f:

        f.write(
            json.dumps(
                row,
                ensure_ascii=False,
            )
            + "\n"
        )

    return {
        "status": "saved"
    }