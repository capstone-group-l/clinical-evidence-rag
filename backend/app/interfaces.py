from typing import Protocol

from app.schemas import GeneratedAnswer, RetrievedPassage


class Retriever(Protocol):
    def retrieve(
        self, question: str, k: int = 5
    ) -> list[RetrievedPassage]: ...


class Generator(Protocol):
    def generate(
        self, question: str, passages: list[RetrievedPassage]
    ) -> GeneratedAnswer: ...


class Verifier(Protocol):
    def verify(
        self, generated: GeneratedAnswer, passages: list[RetrievedPassage]
    ) -> bool: ...


class Reranker(Protocol):
    def rerank(
        self, question: str, passages: list[RetrievedPassage]
    ) -> list[RetrievedPassage]: ...
