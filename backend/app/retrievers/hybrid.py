import logging
from typing import Literal, TypedDict

from app.fakes import FakeReranker
from app.interfaces import Reranker, Retriever
from app.rerankers import rerank_top_k
from app.schemas import RetrievedPassage

logger = logging.getLogger(__name__)

DENSE_WEIGHT = 0.5
BM25_WEIGHT = 0.5


class FusedPassage(TypedDict):
    passage: RetrievedPassage
    score: float
    ranks: dict[str, int]
    found_by: Literal["dense", "bm25", "both"]


# The function will be used to create a new RetrievedPassage with the
# updated score
def with_score(passage: RetrievedPassage, score: float) -> RetrievedPassage:
    return passage.model_copy(update={"score": score})


# Min-max scales a score to 0-1 within its own result list.
def normalize(score: float, lowest: float, highest: float) -> float:
    if highest == lowest:
        return 1.0
    return (score - lowest) / (highest - lowest)


# This function will fuse the results from dense and bm25
def fuse(
    dense_list: list[RetrievedPassage],
    bm25_list: list[RetrievedPassage],
    dense_weight: float = DENSE_WEIGHT,
    bm25_weight: float = BM25_WEIGHT,
) -> list[FusedPassage]:
    passages = {}
    ranks = {}
    scores = {}
    source_scores = {}

    for source_name, results, weight in [
        ("dense", dense_list, dense_weight),
        ("bm25", bm25_list, bm25_weight),
    ]:
        raw_scores = [passage.score for passage in results]
        rank = 0
        for passage in results:
            rank += 1
            chunk_id = passage.chunk.id
            if chunk_id not in passages:
                passages[chunk_id] = passage
                ranks[chunk_id] = {}
                scores[chunk_id] = 0.0
                source_scores[chunk_id] = {}
            if source_name in ranks[chunk_id]:
                continue
            ranks[chunk_id][source_name] = rank
            source_scores[chunk_id][source_name] = passage.score
            scores[chunk_id] += weight * normalize(
                passage.score, min(raw_scores), max(raw_scores)
            )

    rows = []
    for chunk_id in passages:
        best_rank = min(ranks[chunk_id].values())
        rows.append((-scores[chunk_id], best_rank, chunk_id))
    rows.sort()

    merged = []
    for row in rows:
        chunk_id = row[2]
        if "dense" in ranks[chunk_id] and "bm25" in ranks[chunk_id]:
            found_by = "both"
        elif "dense" in ranks[chunk_id]:
            found_by = "dense"
        else:
            found_by = "bm25"
        merged.append(
            {
                "passage": passages[chunk_id],
                "score": scores[chunk_id],
                "ranks": ranks[chunk_id],
                "found_by": found_by,
            }
        )
    return merged


class HybridRetriever:
    def __init__(
        self,
        dense: Retriever,
        bm25: Retriever,
        reranker: Reranker | None = None,
        candidates: int = 30,
        rerank_candidates: int = 20,
        top_k: int = 5,
        dense_weight: float = DENSE_WEIGHT,
        bm25_weight: float = BM25_WEIGHT,
    ) -> None:
        self.dense = dense
        self.bm25 = bm25
        # FakeReranker keeps the fusion order.
        self.reranker = reranker or FakeReranker()
        self.candidates = candidates
        self.rerank_candidates = rerank_candidates
        self.top_k = top_k
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight

    def retrieve(
        self, question: str, k: int | None = None
    ) -> list[RetrievedPassage]:
        if k is None:
            k = self.top_k

        dense_list = self.dense.retrieve(question, self.candidates)
        bm25_list = self.bm25.retrieve(question, self.candidates)
        merged = fuse(
            dense_list, bm25_list, self.dense_weight, self.bm25_weight
        )

        details = {}
        for item in merged:
            details[item["passage"].chunk.id] = item

        fused = []
        for item in merged:
            fused.append(with_score(item["passage"], item["score"]))
        result = rerank_top_k(
            self.reranker, question, fused, self.rerank_candidates, k
        )

        position = 0
        for passage in result:
            position += 1
            item = details[passage.chunk.id]
            logger.info(
                "hybrid position=%d chunk=%s found_by=%s "
                "dense_rank=%d bm25_rank=%d",
                position,
                passage.chunk.id,
                item["found_by"],
                item["ranks"].get("dense", -1),
                item["ranks"].get("bm25", -1),
            )
        return result
