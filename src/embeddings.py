from sentence_transformers import SentenceTransformer

import numpy as np


class EmbeddingEngine:

    def __init__(
        self,
        model_name,
        device="cpu",
    ):

        self.model = SentenceTransformer(
            model_name,
            device=device,
        )

        # NEW API
        self.dim = (
            self.model.get_embedding_dimension()
        )

    # ─────────────────────────────────────────────────────────
    # Embed Multiple Documents
    # ─────────────────────────────────────────────────────────

    def embed_documents(
        self,
        texts,
        batch_size=16,
    ):

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        embeddings = np.array(
            embeddings,
            dtype="float32",
        )

        return embeddings

    # ─────────────────────────────────────────────────────────
    # Embed Single Query
    # ─────────────────────────────────────────────────────────

    def embed_query(self, text):

        embedding = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        embedding = np.array(
            embedding,
            dtype="float32",
        )

        return embedding