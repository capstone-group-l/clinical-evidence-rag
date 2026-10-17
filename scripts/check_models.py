import time

from transformers import (
    AutoModel,
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

CHECKS = [
    ("ncbi/MedCPT-Query-Encoder", AutoModel),
    ("ncbi/MedCPT-Article-Encoder", AutoModel),
    ("ncbi/MedCPT-Cross-Encoder", AutoModelForSequenceClassification),
    ("cross-encoder/nli-deberta-v3-base", AutoModelForSequenceClassification),
]

for name, model_class in CHECKS:
    start = time.time()
    AutoTokenizer.from_pretrained(name)
    model_class.from_pretrained(name)
    print(f"loaded {name} in {time.time() - start:.1f}s")
