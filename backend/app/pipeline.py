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
        raise NotImplementedError(
            "openai generator will be implemented in the near future"
        )
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
