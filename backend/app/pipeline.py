from dataclasses import dataclass
from functools import lru_cache

from app.config import Settings
from app.fakes import AlwaysPassVerifier, FakeRetriever, StubGenerator
from app.interfaces import Generator, Retriever, Verifier


@dataclass
class Pipeline:
    retriever: Retriever
    generator: Generator
    verifier: Verifier


def _build_retriever(settings: Settings) -> Retriever:
    if settings.retriever_mode == "dense":
        raise NotImplementedError(
            "dense retriever will be implemented in the near future"
        )
    return FakeRetriever()


def _build_generator(settings: Settings) -> Generator:
    if settings.llm_mode == "openai":
        from openai import OpenAI

        from app.generators.openai_generator import OpenAIGenerator

        key = settings.openai_api_key
        if key is None:
            raise RuntimeError("OpenAI API key is not set in settings")
        client = OpenAI(api_key=key.get_secret_value(), timeout=30)
        return OpenAIGenerator(client)
    return StubGenerator()


def build_pipeline(settings: Settings | None = None) -> Pipeline:
    settings = settings or Settings()
    return Pipeline(
        _build_retriever(settings),
        _build_generator(settings),
        AlwaysPassVerifier(),
    )


# Built once and reused, so heavy models are not loaded per request.
@lru_cache
def get_pipeline() -> Pipeline:
    return build_pipeline()
