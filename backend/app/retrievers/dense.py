import psycopg
import torch
from app.schemas import Chunk, RetrievedPassage
from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "ncbi/MedCPT-Query-Encoder"
OPERATORS = {"cosine": "<=>", "euclidean": "<->", "inner_product": "<#>"}


class DenseRetriever:
    def __init__(self, database_url: str, distance: str = "cosine"):
        if distance not in OPERATORS:
            raise ValueError(f"Invalid distance metric: {distance}")
        self.distance = distance
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
        # dist is the SQL expression for the distance metric used
        dist = f"c.embedding {OPERATORS[self.distance]} %(qvec)s::vector"
        # score is the number returned for every passage
        # 1 - dist for cosine to get similarity
        # -dist for euclidean so a smaller distance gets a higher score
        # -dist for inner product because it gives the negative inner product
        score = f"1 - ({dist})" if self.distance == "cosine" else f"-({dist})"

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT c.id, c.document_id, d.title, c.text, c.position,
                           d.source_url, d.publish_date,
                           {score} AS score
                    FROM chunks AS c
                    JOIN documents AS d ON d.id = c.document_id
                    ORDER BY {dist}
                    LIMIT %(k)s
                    """,
                    {"qvec": vector, "k": k},
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
                score=row[7],
            )
            for row in results
        ]
