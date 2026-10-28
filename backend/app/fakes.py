from app.schemas import Chunk, GeneratedAnswer, RetrievedPassage


def _fake_passage(position: int) -> RetrievedPassage:
    chunk = Chunk(
        id=f"fake:{position:04d}",
        document_id="fake",
        title="Fake document",
        text=f"This is fake passage {position}.",
        position=position,
        source_url="https://example.org/fake",
        publish_date="2024-01-01",
    )
    return RetrievedPassage(chunk=chunk, score=1.0 - position / 10)


# Returns fixed passages. A question with 'unknown' gets none.
class FakeRetriever:
    def retrieve(self, question: str, k: int = 5) -> list[RetrievedPassage]:
        if "unknown" in question.lower():
            return []
        return [_fake_passage(i) for i in range(min(k, 3))]


# Answers from the first passage without calling any LLM.
class StubGenerator:
    def generate(
        self, question: str, passages: list[RetrievedPassage]
    ) -> GeneratedAnswer:
        if not passages:
            return GeneratedAnswer(text="", cited_chunk_ids=[])
        first = passages[0].chunk
        return GeneratedAnswer(
            text=f"Stub answer based on: {first.text}",
            cited_chunk_ids=[first.id],
        )


# Placeholder for the NLI claim check (Week 4).
class AlwaysPassVerifier:
    def verify(
        self, generated: GeneratedAnswer, passages: list[RetrievedPassage]
    ) -> bool:
        return True
