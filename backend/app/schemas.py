from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# One passage of a source document.
class Chunk(BaseModel):
    id: str
    document_id: str
    title: str
    text: str
    position: int = Field(ge=0)
    source_url: str | None = None
    publish_date: date | None = None


# A chunk returned by a Retriever, with its score.
class RetrievedPassage(BaseModel):
    chunk: Chunk
    score: float


# A reference from an answer to one retrieved chunk.
class Citation(BaseModel):
    chunk_id: str


# Raw Generator output.
class GeneratedAnswer(BaseModel):
    text: str
    cited_chunk_ids: list[str]
    tokens_used: int | None = None


# POST /v1/query body. Out-of-range lengths get a 422.
class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


# POST /v1/query returns. Ensures that sources are the cited passages.
class AnswerResponse(BaseModel):
    status: Literal["answered", "insufficient_evidence"]
    answer: str | None = None
    citations: list[Citation] = []
    sources: list[RetrievedPassage] = []
    tokens_used: int | None = Field(
        default=None, exclude_if=lambda value: value is None
    )

    @model_validator(mode="after")
    def check_status_rules(self) -> "AnswerResponse":
        if self.status == "answered":
            if not self.answer or not self.citations:
                raise ValueError("answered needs an answer and one citation")
        elif self.answer or self.citations:
            raise ValueError(
                "insufficient_evidence has no answer or citations"
            )
        return self
