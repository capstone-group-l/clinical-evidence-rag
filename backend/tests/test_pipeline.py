from app.config import Settings
from app.fakes import FakeRetriever, StubGenerator
from app.pipeline import build_pipeline


def fake_settings() -> Settings:
    return Settings(retriever_mode="fake", llm_mode="stub")


def test_default_pipeline_uses_fakes():
    pipeline = build_pipeline(fake_settings())
    assert isinstance(pipeline.retriever, FakeRetriever)
    assert isinstance(pipeline.generator, StubGenerator)


def test_stub_answer_cites_a_retrieved_passage():
    pipeline = build_pipeline(fake_settings())
    passages = pipeline.retriever.retrieve("What is X?")
    generated = pipeline.generator.generate("What is X?", passages)
    assert generated.cited_chunk_ids == [passages[0].chunk.id]


def test_fake_retriever_returns_nothing_for_unknown():
    assert FakeRetriever().retrieve("an unknown topic") == []
