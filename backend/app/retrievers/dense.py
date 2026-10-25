import psycopg
import torch
from app.schemas import Chunk, RetrievedPassage
from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "ncbi/MedCPT-Query-Encoder"


class DenseRetriever:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).eval()

    def embed(self, text: str) -> list[float]:
        inputs = self.tokenizer(
            text,
            truncation=True,
            return_tensors="pt",
            max_length=64,
        )
        with torch.no_grad():
            output = self.model(**inputs).last_hidden_state[:, 0, :]
        return output[0].tolist()

    def retrieve(self, question: str, k: int = 5) -> list[RetrievedPassage]:
        if k < 1:
            raise ValueError("k must be greater than zero")

        embedding = self.embed(question)
        vector = "[" + ",".join(f"{value:.6f}" for value in embedding) + "]"

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.document_id, d.title, c.text, c.position,
                           d.source_url, d.publish_date,
                           c.embedding <=> %s::vector AS distance
                    FROM chunks AS c
                    JOIN documents AS d ON d.id = c.document_id
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vector, vector, k),
                )
                results = cur.fetchall()
        return [
            RetrievedPassage(
                chunk=Chunk(
                    id=row[0],
                    document_id=row[1],
                    title=row[2],
                    text=row[3],
                    position=row[4],
                    source_url=row[5],
                    publish_date=row[6],
                ),
                score=1.0 - row[7],
            )
            for row in results
        ]
