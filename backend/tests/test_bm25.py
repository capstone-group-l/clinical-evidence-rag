from app.retrievers.bm25 import BM25Retriever, tokenize
from app.schemas import Chunk


def make_chunk(i: int, text: str) -> Chunk:
    return Chunk(
        id=f"doc:{i:04d}",
        document_id="doc",
        title="Example",
        text=text,
        position=i,
    )


CHUNKS = [
    make_chunk(0, "Aspirin reduces cardiovascular events."),
    make_chunk(1, "Metformin is first-line therapy for type 2 diabetes."),
    make_chunk(2, "Donepezil is used to treat Alzheimer's disease."),
]


def test_tokenize_splits_possessives_and_hyphens():
    assert tokenize("Alzheimer's anti-inflammatory") == [
        "alzheimer's",
        "alzheimer",
        "anti-inflammatory",
        "anti",
        "inflammatory",
    ]


def test_retrieves_matching_chunk():
    results = BM25Retriever(CHUNKS).retrieve("treatment for diabetes")
    assert [r.chunk.id for r in results] == ["doc:0001"]


def test_possessive_matches_plain_word():
    results = BM25Retriever(CHUNKS).retrieve("alzheimer")
    assert [r.chunk.id for r in results] == ["doc:0002"]


def test_no_match_returns_nothing():
    assert BM25Retriever(CHUNKS).retrieve("unknown topic") == []
    assert BM25Retriever([]).retrieve("diabetes") == []


ACRONYM_CHUNKS = [
    make_chunk(0, "A cat scratch can cause infection."),
    make_chunk(1, "A CAT scan showed no bleeding."),
    make_chunk(2, "NSAID use increases bleeding risk."),
    make_chunk(3, "Metformin lowers HbA1c in type 2 diabetes."),
]


def test_tokenize_keeps_acronym_case():
    assert tokenize("CAT") == ["cat", "CAT"]
    assert tokenize("COVID-19") == [
        "covid-19",
        "covid",
        "19",
        "COVID-19",
        "COVID",
    ]
    assert "CAT" not in tokenize("Cat scratch")


def test_tokenize_strips_acronym_suffixes():
    assert "NSAID" in tokenize("NSAIDs")
    assert "COPD" in tokenize("COPD's")


def test_acronym_beats_common_word():
    results = BM25Retriever(ACRONYM_CHUNKS).retrieve("CAT")
    assert results[0].chunk.id == "doc:0001"
