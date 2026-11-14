import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

DEVSET_FILE = ROOT / "eval" / "devset.jsonl"
RUNS_DIR = ROOT / "eval" / "runs"
TOP_K = 10

# Each setup is a set of environment variables
SETUPS = {
    "dense_cosine": {
        "RETRIEVER_MODE": "dense",
        "DENSE_DISTANCE": "cosine",
        "RERANK_MODE": "off",
    },
    "dense_inner_product": {
        "RETRIEVER_MODE": "dense",
        "DENSE_DISTANCE": "inner_product",
        "RERANK_MODE": "off",
    },
    "dense_euclidean": {
        "RETRIEVER_MODE": "dense",
        "DENSE_DISTANCE": "euclidean",
        "RERANK_MODE": "off",
    },
    "bm25": {
        "RETRIEVER_MODE": "bm25",
        "RERANK_MODE": "off",
    },
    "hybrid": {
        "RETRIEVER_MODE": "hybrid",
        "DENSE_DISTANCE": "cosine",
        "RERANK_MODE": "off",
    },
    "hybrid_rerank": {
        "RETRIEVER_MODE": "hybrid",
        "DENSE_DISTANCE": "cosine",
        "RERANK_MODE": "crossencoder",
    },
}


def load_questions():
    questions = []
    lines = DEVSET_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip() == "":
            continue
        questions.append(json.loads(line))
    return questions


def run_setup(setup_name):
    if setup_name not in SETUPS:
        print(f"Unknown setup '{setup_name}'. Choose one of: {list(SETUPS)}")
        sys.exit(1)

    os.environ["LLM_MODE"] = "stub"
    for name, value in SETUPS[setup_name].items():
        os.environ[name] = value

    from app.config import Settings
    from app.pipeline import build_pipeline

    retriever = build_pipeline(Settings()).retriever
    questions = load_questions()

    # Warm-up query so model loading is not counted in the timing
    retriever.retrieve(questions[0]["question"], k=TOP_K)

    results = []
    for question in questions:
        start = time.perf_counter()
        passages = retriever.retrieve(question["question"], k=TOP_K)
        seconds = time.perf_counter() - start

        chunk_ids = []
        for passage in passages:
            chunk_ids.append(passage.chunk.id)

        if len(chunk_ids) < TOP_K:
            print(f"note: {question['id']} returned {len(chunk_ids)} chunks")

        results.append(
            {
                "id": question["id"],
                "chunk_ids": chunk_ids,
                "seconds": round(seconds, 3),
            }
        )

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = RUNS_DIR / f"{setup_name}.json"
    output_file.write_text(
        json.dumps(results, indent=1) + "\n", encoding="utf-8"
    )
    print(f"saved {output_file}")


def show_pool(question_id):

    pool = set()
    for run_file in RUNS_DIR.glob("*.json"):
        results = json.loads(run_file.read_text(encoding="utf-8"))
        for result in results:
            if result["id"] == question_id:
                for chunk_id in result["chunk_ids"]:
                    pool.add(chunk_id)

    if not pool:
        print(f"No saved runs contain question '{question_id}'.")
        return

    question_text = None
    for question in load_questions():
        if question["id"] == question_id:
            question_text = question["question"]

    import psycopg
    from app.config import Settings

    with psycopg.connect(Settings().database_url) as conn:
        rows = conn.execute(
            "SELECT id, text FROM chunks WHERE id = ANY(%s) ORDER BY id",
            (sorted(pool),),
        ).fetchall()

    print(question_text)
    print(f"{len(rows)} candidates")
    for chunk_id, text in rows:
        print("-" * 80)
        print(chunk_id)
        print(text)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("run", "pool"):
        print("usage: python eval/run_retrieval.py run <setup>")
        print("       python eval/run_retrieval.py pool <question_id>")
        print(f"setups: {', '.join(SETUPS)}")
        sys.exit(1)

    if sys.argv[1] == "run":
        run_setup(sys.argv[2])
    else:
        show_pool(sys.argv[2])
