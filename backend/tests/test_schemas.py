import pytest
from app.schemas import AnswerResponse, Chunk, Citation, RetrievedPassage
from pydantic import ValidationError


def make_source() -> RetrievedPassage:
    chunk = Chunk(
        id="doc01:0000",
        document_id="doc01",
        title="Example",
        text="Example text.",
        position=0,
    )
    return RetrievedPassage(chunk=chunk, score=0.9)


def test_answered_response_is_valid():
    response = AnswerResponse(
        status="answered",
        answer="Example answer.",
        citations=[Citation(chunk_id="doc01:0000")],
        sources=[make_source()],
    )
    assert response.status == "answered"


def test_answered_without_citation_is_rejected():
    with pytest.raises(ValidationError):
        AnswerResponse(status="answered", answer="Example answer.")


def test_insufficient_evidence_is_valid_when_empty():
    response = AnswerResponse(status="insufficient_evidence")
    assert response.answer is None


def test_insufficient_evidence_with_answer_is_rejected():
    with pytest.raises(ValidationError):
        AnswerResponse(status="insufficient_evidence", answer="Text")


def test_unknown_status_is_rejected():
    with pytest.raises(ValidationError):
        AnswerResponse(status="maybe")
