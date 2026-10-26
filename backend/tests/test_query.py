import pytest
from app.fakes import AlwaysPassVerifier, FakeRetriever, StubGenerator
from app.main import app
from app.pipeline import Pipeline, get_pipeline
from app.schemas import GeneratedAnswer
from fastapi.testclient import TestClient

client = TestClient(app)

INSUFFICIENT = {
    "status": "insufficient_evidence",
    "answer": None,
    "citations": [],
    "sources": [],
    "token_count": None,
}


# Generator that returns a fixed answer.
class FixedGenerator:
    def __init__(self, generated: GeneratedAnswer):
        self.generated = generated

    def generate(self, question, passages):
        return self.generated


class RejectingVerifier:
    def verify(self, generated, passages):
        return False


def use_pipeline(generator=None, verifier=None):
    app.dependency_overrides[get_pipeline] = lambda: Pipeline(
        FakeRetriever(),
        generator or StubGenerator(),
        verifier or AlwaysPassVerifier(),
    )


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def post(question: str):
    return client.post("/v1/query", json={"question": question})


def test_answers_with_cited_sources():
    response = post("What is X?")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "answered"
    assert body["answer"]
    assert body["citations"] == [{"chunk_id": "fake:0000"}]
    assert [s["chunk"]["id"] for s in body["sources"]] == ["fake:0000"]
    assert body["token_count"] is None


def test_token_count_is_returned_from_generator():
    use_pipeline(
        generator=FixedGenerator(
            GeneratedAnswer(
                text="Answer.",
                cited_chunk_ids=["fake:0000"],
                token_count=123,
            )
        )
    )

    assert post("What is X?").json()["token_count"] == 123


def test_short_question_is_rejected():
    assert post("hi").status_code == 422


def test_no_passages_is_insufficient():
    response = post("an unknown topic")

    assert response.status_code == 200
    assert response.json() == INSUFFICIENT


@pytest.mark.parametrize("cited", [["fake:9999"], []])
def test_bad_citations_are_insufficient(cited):
    use_pipeline(
        generator=FixedGenerator(
            GeneratedAnswer(text="A.", cited_chunk_ids=cited)
        )
    )

    assert post("What is X?").json() == INSUFFICIENT


def test_rejected_by_verifier_is_insufficient():
    use_pipeline(verifier=RejectingVerifier())

    assert post("What is X?").json() == INSUFFICIENT


def test_duplicate_citations_are_removed_in_order():
    use_pipeline(
        generator=FixedGenerator(
            GeneratedAnswer(
                text="Answer.",
                cited_chunk_ids=["fake:0002", "fake:0000", "fake:0002"],
            )
        )
    )

    body = post("What is X?").json()

    assert body["citations"] == [
        {"chunk_id": "fake:0002"},
        {"chunk_id": "fake:0000"},
    ]
    assert [s["chunk"]["id"] for s in body["sources"]] == [
        "fake:0002",
        "fake:0000",
    ]
