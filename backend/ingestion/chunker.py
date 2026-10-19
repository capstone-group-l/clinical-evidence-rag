from app.schemas import Chunk


def chunk_text(
    document_id: str,
    title: str,
    text: str,
    size: int = 200,
    overlap: int = 30,
) -> list[Chunk]:
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and < size")

    words = text.split()
    chunks: list[Chunk] = []
    step = size - overlap

    for position, start in enumerate(range(0, len(words), step)):
        chunk_words = words[start : start + size]
        chunk = Chunk(
            id=f"{document_id}:{position:04d}",
            document_id=document_id,
            title=title,
            text=" ".join(chunk_words),
            position=position,
        )
        chunks.append(chunk)
        if start + size >= len(words):
            break

    return chunks
