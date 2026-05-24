import config

from src.data_loader import (
    load_excel,
    tokenize,
)

from src.embeddings import (
    EmbeddingEngine,
)

from src.generator import (
    AnswerGenerator,
)

from src.retrieval import (
    HybridRetriever,
)

from src.query_expansion import (
    expand_query,
)

from src.utils import (
    sanitize_query,
)


class RAGPipeline:

    def __init__(self):

        self.embedder = EmbeddingEngine(
            config.EMBEDDING_MODEL,
            device=config.EMBEDDING_DEVICE,
        )

        self.generator = AnswerGenerator()

        self.retriever = None

    # ─────────────────────────────────────────────────────
    # Build Index
    # ─────────────────────────────────────────────────────

    def build_index(self, data_path):

        records = load_excel(data_path)

        texts = [
            r.content
            for r in records
        ]

        embeddings = (
            self.embedder.embed_documents(
                texts
            )
        )

        self.retriever = HybridRetriever(
            records,
            embeddings,
        )

        self.retriever.save(
            config.FAISS_INDEX,
            config.BM25_PATH,
            config.METADATA_PATH,
        )

    # ─────────────────────────────────────────────────────
    # Load Index
    # ─────────────────────────────────────────────────────

    def load_index(self):

        self.retriever = (
            HybridRetriever.load(
                config.FAISS_INDEX,
                config.BM25_PATH,
                config.METADATA_PATH,
            )
        )

    # ─────────────────────────────────────────────────────
    # Answer Question
    # ─────────────────────────────────────────────────────

    def answer(self, query):

        query = sanitize_query(query)

        expanded_queries = expand_query(query)

        all_results = []

        for q in expanded_queries:

            query_vector = (
                self.embedder.embed_query(q)
            )

            query_tokens = tokenize(q)

            hits = self.retriever.search(
                query_vector=query_vector,
                query_tokens=query_tokens,
                top_k=config.TOP_K_RETRIEVAL,
                dense_weight=config.DENSE_WEIGHT,
                bm25_weight=config.BM25_WEIGHT,
            )

            all_results.extend(hits)

        unique = {}

        for r in all_results:

            if (
                r.answer not in unique
                or
                r.score > unique[r.answer].score
            ):
                unique[r.answer] = r

        final_hits = list(unique.values())

        final_hits.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        final_hits = final_hits[
            :config.TOP_K_FINAL
        ]

        result = self.generator.generate(
            query,
            final_hits,
            min_confidence=config.MIN_CONFIDENCE,
        )

        return result