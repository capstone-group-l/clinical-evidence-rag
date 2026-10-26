from types import SimpleNamespace

from app.fakes import FakeRetriever
from app.generators.openai_generator import OpenAIGenerator
from app.schemas import GeneratedAnswerContent


class FakeCompletions:
    def __init__(self):
        self.response_format = None

    def parse(self, **kwargs):
        self.response_format = kwargs["response_format"]
        return SimpleNamespace(
            usage=SimpleNamespace(
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
            ),
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        refusal=None,
                        parsed=GeneratedAnswerContent(
                            text="Answer.",
                            cited_chunk_ids=["fake:0000"],
                        ),
                    )
                )
            ],
        )


def test_token_count_is_added_after_model_parsing():
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    generator = OpenAIGenerator(client)

    result = generator.generate(
        "What is X?", FakeRetriever().retrieve("What is X?")
    )

    assert completions.response_format is GeneratedAnswerContent
    assert result.text == "Answer."
    assert result.cited_chunk_ids == ["fake:0000"]
    assert result.token_count == 15
