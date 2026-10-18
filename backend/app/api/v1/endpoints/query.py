from fastapi import APIRouter, Depends

from app.pipeline import Pipeline, get_pipeline
from app.schemas import AnswerResponse, Citation, QueryRequest
from app.validation import validate_citation_ids

router = APIRouter()


# Returns a grounded answer with citations, or insufficient_evidence.
@router.post(
    "/query",
    response_model=AnswerResponse,
    summary="Answer a Clinical Question",
)
def post_query(
    request: QueryRequest,
    pipeline: Pipeline = Depends(get_pipeline),
) -> AnswerResponse:
    passages = pipeline.retriever.retrieve(request.question)
    if not passages:
        return AnswerResponse(status="insufficient_evidence")

    generated = pipeline.generator.generate(request.question, passages)
    if validate_citation_ids(generated, passages):
        return AnswerResponse(status="insufficient_evidence")

    if not pipeline.verifier.verify(generated, passages):
        return AnswerResponse(status="insufficient_evidence")

    # Drop duplicate IDs, keeping their order.
    cited_ids = list(dict.fromkeys(generated.cited_chunk_ids))
    by_id = {p.chunk.id: p for p in passages}
    return AnswerResponse(
        status="answered",
        answer=generated.text,
        citations=[Citation(chunk_id=i) for i in cited_ids],
        sources=[by_id[i] for i in cited_ids],
    )
