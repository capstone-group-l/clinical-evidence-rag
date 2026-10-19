import pytest
from ingestion.chunker import chunk_text


def words(count: int) -> str:
    return " ".join(f"w{i}" for i in range(count))


def test_empty_text_gives_no_chunks():
    assert chunk_text("PMC10383547", "Example", "") == []
    assert chunk_text("PMC10383547", "Example", "   \n\t ") == []


def test_short_text_gives_one_chunk():
    chunks = chunk_text(
        "PMC10383547", "Example", words(50), size=200, overlap=30
    )
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.id == "PMC10383547:0000"
    assert chunk.document_id == "PMC10383547"
    assert chunk.title == "Example"
    assert chunk.position == 0
    assert chunk.text == words(50)


def test_long_text_ids_and_positions():
    chunks = chunk_text(
        "PMC10383547", "Example", words(25), size=10, overlap=3
    )
    assert [c.id for c in chunks] == [
        "PMC10383547:0000",
        "PMC10383547:0001",
        "PMC10383547:0002",
        "PMC10383547:0003",
    ]
    assert [c.position for c in chunks] == [0, 1, 2, 3]


def test_consecutive_chunks_share_overlap():
    chunks = chunk_text(
        "PMC10383547", "Example", words(25), size=10, overlap=3
    )
    for prev, curr in zip(chunks, chunks[1:]):
        assert prev.text.split()[-3:] == curr.text.split()[:3]


def test_long_text_covers_every_word():
    text = words(25)
    chunks = chunk_text("PMC10383547", "Example", text, size=10, overlap=3)
    assert chunks[-1].text.split()[-1] == "w24"
    covered = {w for c in chunks for w in c.text.split()}
    assert covered == set(text.split())


def test_same_input_gives_same_chunks():
    text = words(25)
    first = chunk_text("PMC10383547", "Example", text, size=10, overlap=3)
    second = chunk_text("PMC10383547", "Example", text, size=10, overlap=3)
    assert first == second


@pytest.mark.parametrize("overlap", [10, 15, -1])
def test_bad_overlap_is_rejected(overlap: int):
    with pytest.raises(ValueError):
        chunk_text(
            "PMC10383547", "Example", words(50), size=10, overlap=overlap
        )


@pytest.mark.parametrize("size", [0, -5])
def test_bad_size_is_rejected(size: int):
    with pytest.raises(ValueError):
        chunk_text("PMC10383547", "Example", words(50), size=size, overlap=0)
