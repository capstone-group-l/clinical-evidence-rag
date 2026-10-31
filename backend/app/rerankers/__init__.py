from app.config import Settings
from app.fakes import FakeReranker
from app.interfaces import Reranker
from app.schemas import RetrievedPassage


def build_reranker(settings: Settings) -> Reranker:
    if settings.rerank_mode == "crossencoder":
        from app.rerankers.crossencoder import MedCPTReranker

        return MedCPTReranker()
    return FakeReranker()


def rerank_top_k(
    reranker: Reranker,
    question: str,
    passages: list[RetrievedPassage],
    candidates: int,
    top_k: int,
) -> list[RetrievedPassage]:
    pool = passages[:candidates]
    if pool:
        return reranker.rerank(question, pool)[:top_k]
    return []
