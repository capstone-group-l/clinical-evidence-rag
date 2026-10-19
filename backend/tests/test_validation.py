from app.schemas import Chunk, GeneratedAnswer, RetrievedPassage
from app.validation import validate_citation_ids


def passage(chunk_id: str) -> RetrievedPassage:
    chunk = Chunk(
        id=chunk_id,
        document_id="PMC10383547",
        title="Example",
        text="text text text",
        position=0,
    )
    return RetrievedPassage(chunk=chunk, score=1.0)


def test_valid_ids_have_no_problems():
    generated = GeneratedAnswer(text="A", cited_chunk_ids=["PMC10383547:0000"])
    assert (
        validate_citation_ids(generated, [passage("PMC10383547:0000")]) == []
    )


def test_unknown_id_is_a_problem():
    generated = GeneratedAnswer(text="A", cited_chunk_ids=["PMC6360702:0001"])
    problems = validate_citation_ids(generated, [passage("PMC10383547:0000")])
    assert problems == ["unknown chunk id: PMC6360702:0001"]


def test_no_citations_is_a_problem():
    generated = GeneratedAnswer(text="A", cited_chunk_ids=[])
    problems = validate_citation_ids(generated, [passage("PMC10383547:0000")])
    assert problems == ["no citations"]


def test_ids_must_match_exactly():
    generated = GeneratedAnswer(text="A", cited_chunk_ids=["pmc10383547:0000"])
    assert (
        validate_citation_ids(generated, [passage("PMC10383547:0000")]) != []
    )
