import logging

from openai import OpenAI

from app.schemas import GeneratedAnswer, RetrievedPassage

MODEL = "gpt-4o-mini"
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You answer clinical questions using ONLY and EXCLUSIVELY the passages "
    "provided. Each passage starts with its ID in square brackets. Cite the "
    "ID of every passage you use, exactly as written. If the passages do not "
    "answer the question, return an empty answer and no IDs. Do not use "
    "outside knowledge."
)


# This will be used to generate answers.
class OpenAIGenerator:
    def __init__(self, client: OpenAI) -> None:
        self.client = client

    def generate(
        self, question: str, passages: list[RetrievedPassage]
    ) -> GeneratedAnswer:
        context = "\n\n".join(
            f"[{p.chunk.id}] {p.chunk.text}" for p in passages
        )

        user_message = f"Passages:\n{context}\n\nQuestion: {question}"
        completion = self.client.chat.completions.parse(
            model=MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format=GeneratedAnswer,
        )
        # Log token usage
        usage = completion.usage
        if usage is not None:
            logger.info(
                "tokens in=%s out=%s",
                usage.prompt_tokens,
                usage.completion_tokens,
            )
        # Return the parsed answer, or an empty one if there is none
        message = completion.choices[0].message
        if message.refusal or message.parsed is None:
            return GeneratedAnswer(text="", cited_chunk_ids=[])
        return message.parsed
