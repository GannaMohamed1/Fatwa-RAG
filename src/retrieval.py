import pickle
from dataclasses import dataclass

import faiss
import numpy as np

from rank_bm25 import BM25Okapi


# ─────────────────────────────────────────────────────────────
# Search Result
# ─────────────────────────────────────────────────────────────

@dataclass
class SearchResult:
    question: str
    answer: str
    score: float


# ─────────────────────────────────────────────────────────────
# Hybrid Retriever
# ─────────────────────────────────────────────────────────────

class HybridRetriever:

    def __init__(
        self,
        records,
        embeddings,
    ):

        self.records = records

        self.embeddings = embeddings

        dim = embeddings.shape[1]

        # FAISS index

        self.index = faiss.IndexFlatIP(dim)

        self.index.add(embeddings)

        # BM25

        corpus_tokens = [
            r.tokens
            for r in records
        ]

        self.bm25 = BM25Okapi(
            corpus_tokens
        )

    # ─────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────

    def search(
        self,
        query_vector,
        query_tokens,
        top_k=10,
        dense_weight=0.75,
        bm25_weight=0.25,
    ):

        # Dense Search

        dense_scores, dense_idx = (
            self.index.search(
                query_vector,
                top_k,
            )
        )

        dense_scores = dense_scores[0]

        dense_idx = dense_idx[0]

        # Sparse Search

        bm25_scores = (
            self.bm25.get_scores(
                query_tokens
            )
        )

        bm25_scores = np.array(
            bm25_scores
        )

        # Normalize BM25

        if bm25_scores.max() > 0:

            bm25_scores = (
                bm25_scores
                /
                bm25_scores.max()
            )

        # Combine Scores

        results = []

        used = set()

        for idx, dense_score in zip(
            dense_idx,
            dense_scores,
        ):

            if idx < 0:
                continue

            bm25_score = bm25_scores[idx]

            final_score = (
                dense_weight
                *
                float(dense_score)
                +
                bm25_weight
                *
                float(bm25_score)
            )

            if idx not in used:

                used.add(idx)

                record = self.records[idx]

                results.append(
                    SearchResult(
                        question=record.question,
                        answer=record.answer,
                        score=final_score,
                    )
                )

        # Sort

        results.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return results[:top_k]

    # ─────────────────────────────────────────────────────
    # Save
    # ─────────────────────────────────────────────────────

    def save(
        self,
        faiss_path,
        bm25_path,
        metadata_path,
    ):

        faiss.write_index(
            self.index,
            faiss_path,
        )

        with open(
            bm25_path,
            "wb",
        ) as f:

            pickle.dump(
                self.bm25,
                f,
            )

        with open(
            metadata_path,
            "wb",
        ) as f:

            pickle.dump(
                self.records,
                f,
            )

    # ─────────────────────────────────────────────────────
    # Load
    # ─────────────────────────────────────────────────────

    @classmethod
    def load(
        cls,
        faiss_path,
        bm25_path,
        metadata_path,
    ):

        obj = cls.__new__(cls)

        obj.index = faiss.read_index(
            faiss_path
        )

        with open(
            bm25_path,
            "rb",
        ) as f:

            obj.bm25 = pickle.load(f)

        with open(
            metadata_path,
            "rb",
        ) as f:

            obj.records = pickle.load(f)

        return obj