from dataclasses import dataclass
from functools import lru_cache

from app.config import Settings
from app.fakes import AlwaysPassVerifier, FakeRetriever, StubGenerator
from app.interfaces import Generator, Retriever, Verifier
from app.schemas import Chunk


@dataclass
class Pipeline:
    retriever: Retriever
    generator: Generator
    verifier: Verifier


def _read_chunks(database_url: str) -> list[Chunk]:
    import psycopg
    from psycopg.rows import dict_row

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.document_id, d.title, c.text, c.position,
                   d.source_url, d.publish_date
            FROM chunks AS c
            JOIN documents AS d ON d.id = c.document_id
            """
        ).fetchall()
    return [Chunk(**row) for row in rows]


def _build_retriever(settings: Settings) -> Retriever:
    if settings.retriever_mode != "fake" and not settings.database_url:
        raise ValueError(
            "DATABASE_URL is required when retriever_mode is "
            f"'{settings.retriever_mode}'"
        )

    if settings.retriever_mode == "hybrid":
        from app.rerankers import build_reranker
        from app.retrievers.bm25 import BM25Retriever
        from app.retrievers.dense import DenseRetriever
        from app.retrievers.hybrid import HybridRetriever

        dense = DenseRetriever(
            settings.database_url, distance=settings.dense_distance
        )
        chunks = _read_chunks(settings.database_url)
        bm25 = BM25Retriever(chunks)
        return HybridRetriever(
            dense,
            bm25,
            build_reranker(settings),
            candidates=settings.retriever_candidates,
            rerank_candidates=settings.rerank_candidates,
            top_k=settings.rerank_top_k,
        )

    if settings.retriever_mode == "dense":
        from app.retrievers.dense import DenseRetriever

        return DenseRetriever(
            settings.database_url, distance=settings.dense_distance
        )

    if settings.retriever_mode == "bm25":
        from app.retrievers.bm25 import BM25Retriever

        chunks = _read_chunks(settings.database_url)
        return BM25Retriever(chunks)

    return FakeRetriever()


def _build_generator(settings: Settings) -> Generator:
    if settings.llm_mode == "openai":
        from openai import OpenAI

        from app.generators.openai_generator import OpenAIGenerator

        key = settings.openai_api_key
        if key is None:
            raise RuntimeError("OpenAI API key is not set in settings")
        client = OpenAI(api_key=key.get_secret_value(), timeout=30)
        return OpenAIGenerator(client)
    return StubGenerator()


def build_pipeline(settings: Settings | None = None) -> Pipeline:
    settings = settings or Settings()
    return Pipeline(
        _build_retriever(settings),
        _build_generator(settings),
        AlwaysPassVerifier(),
    )


# Built once and reused, so heavy models are not loaded per request.
@lru_cache
def get_pipeline() -> Pipeline:
    return build_pipeline()
