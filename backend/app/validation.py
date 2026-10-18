from app.schemas import GeneratedAnswer, RetrievedPassage


# Returns a list of problems found from the citations generated.
# An empty list means all citations are valid.
def validate_citation_ids(
    generated: GeneratedAnswer,
    passages: list[RetrievedPassage],
):
    if not generated.cited_chunk_ids:
        return ["no citations"]

    allowed_chunk_ids = set()
    for passage in passages:
        allowed_chunk_ids.add(passage.chunk.id)

    errors = []
    for chunk_id in generated.cited_chunk_ids:
        if chunk_id not in allowed_chunk_ids:
            errors.append(f"unknown chunk id: {chunk_id}")

    return errors
