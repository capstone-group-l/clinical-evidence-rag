import pytest
from app.rerankers import rerank_top_k
from app.schemas import Chunk, RetrievedPassage

QUESTION = "Does metformin lower HbA1c?"


def make_passage(i: int, text: str) -> RetrievedPassage:
    chunk = Chunk(
        id=f"doc:{i:04d}",
        document_id="doc",
        title="Example",
        text=text,
        position=i,
    )
    return RetrievedPassage(chunk=chunk, score=0.0)


# Reverses the passages, so tests can tell it apart from retrieval order.
class ReversingReranker:
    def rerank(self, question, passages):
        return list(reversed(passages))


@pytest.fixture(scope="module")
def reranker():
    pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from app.rerankers.crossencoder import MedCPTReranker

    return MedCPTReranker(batch_size=2)


def test_rerank_top_k_scores_only_candidates_and_returns_top_k():
    passages = [make_passage(i, f"Passage {i}.") for i in range(5)]

    results = rerank_top_k(
        ReversingReranker(), QUESTION, passages, candidates=3, top_k=2
    )

    assert results == [passages[2], passages[1]]


def test_relevant_passage_ranks_first(reranker):
    passages = [
        make_passage(0, "Aspirin is used to treat pain and inflammation."),
        make_passage(1, "A heart attack is a serious medical emergency."),
        make_passage(
            2, "Metformin significantly lowered HbA1c in type 2 diabetes."
        ),
    ]

    results = reranker.rerank(QUESTION, passages)

    assert results[0].chunk.id == "doc:0002"
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_truncation_cuts_passage_end_and_keeps_question(reranker):
    long_text = "aspirin " + "word " * 2000 + "tylenol"

    encoded = reranker.encode(QUESTION, [make_passage(0, long_text)])

    input_ids = encoded["input_ids"]
    assert input_ids.shape[1] == reranker.max_length

    model_input = reranker.tokenizer.decode(input_ids[0])
    assert model_input.startswith(
        "[CLS] does metformin lower hba1c? [SEP] aspirin"
    )
    assert "tylenol" not in model_input
