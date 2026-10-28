import torch
from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "ncbi/MedCPT-Article-Encoder"


class ArticleEmbedder:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).eval()

    def embed(self, pairs: list[list[str]]) -> list[list[float]]:
        with torch.no_grad():
            encoded = self.tokenizer(
                pairs,
                truncation=True,
                padding=True,
                return_tensors="pt",
                max_length=512,
            )
            output = self.model(**encoded).last_hidden_state[:, 0, :]
        return output.tolist()
