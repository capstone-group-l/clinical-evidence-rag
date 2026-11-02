import logging

from app.schemas import RetrievedPassage

logger = logging.getLogger(__name__)
MODEL_NAME = "ncbi/MedCPT-Cross-Encoder"
MAX_LENGTH = 512
BATCH_SIZE = 16


# Log the truncation of passages by setting a warning.
# It helps to identify which chunks are being truncated.
def log_truncated(
    passages: list[RetrievedPassage], lengths: list[int], limit: int
) -> None:
    for passage, length in zip(passages, lengths):
        if length > limit:
            logger.warning(
                "Truncating passage %s to %d tokens (original length: %d)",
                passage.chunk.id,
                limit,
                length,
            )


class MedCPTReranker:
    # Builds the object with the model name, batch size and max length.
    def __init__(
        self,
        model_name=MODEL_NAME,
        batch_size=BATCH_SIZE,
        max_length=MAX_LENGTH,
    ):
        import torch
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
        )

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name
        )
        self.model.eval()
        self.batch_size = batch_size
        self.max_length = max_length

    # Reranks the passages by their relevance to the question.
    def rerank(
        self, question: str, passages: list[RetrievedPassage]
    ) -> list[RetrievedPassage]:
        if not passages:
            return []
        scores = self.score(question, passages)
        ranked = sorted(
            zip(passages, scores), key=lambda p: p[1], reverse=True
        )
        return [RetrievedPassage(chunk=p.chunk, score=s) for p, s in ranked]

    # Tokenizes the pairs. With truncate=False it returns the full token ids.
    def encode(self, question, passages, truncate=True):
        pairs = [[question, p.chunk.text] for p in passages]
        if not truncate:
            return self.tokenizer(pairs, truncation=False, verbose=False)
        return self.tokenizer(
            pairs,
            truncation=True,
            padding=True,
            return_tensors="pt",
            max_length=self.max_length,
        )

    # Scores the passages based on their relevance to the question.
    def score(
        self, question: str, passages: list[RetrievedPassage]
    ) -> list[float]:
        scores = []
        for start in range(0, len(passages), self.batch_size):
            batch = passages[start : start + self.batch_size]

            full = self.encode(question, batch, truncate=False)
            log_truncated(
                batch,
                [len(ids) for ids in full["input_ids"]],
                self.max_length,
            )

            encoded = self.encode(question, batch)

            with self.torch.inference_mode():
                outputs = self.model(**encoded)
                scores.extend(outputs.logits[:, 0].tolist())
        return scores
