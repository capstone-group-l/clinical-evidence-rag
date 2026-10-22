import csv
import json
import os
import time
import urllib.request
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from .chunker import chunk_text
from .embedder import ArticleEmbedder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PROJECT_ROOT / "docs" / "corpus-manifest.csv"
load_dotenv(PROJECT_ROOT / ".env")


def fetch_bioc_document(pmcid: str) -> dict | None:
    url = (
        "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/"
        f"pmcoa.cgi/BioC_json/{pmcid}/unicode"
    )
    request = urllib.request.Request(url)

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as error:
        print(f"Error fetching {pmcid}: {error}")
        return None

    collections = data if isinstance(data, list) else [data]
    for collection in collections:
        raw_date = collection.get("date", "")
        publish_date = None
        if len(raw_date) == 8 and raw_date.isdigit():
            publish_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
        elif len(raw_date) == 10 and raw_date[4] == "-" and raw_date[7] == "-":
            publish_date = raw_date

        for document in collection.get("documents", []):
            license_str = document.get("infons", {}).get("license", "Unknown")
            title = "Unknown Title"
            text_blocks = []

            for passage in document.get("passages", []):
                infons = passage.get("infons", {})
                passage_text = passage.get("text", "").strip()
                if infons.get("section_type") == "REF":
                    break
                if infons.get("section_type") == "TITLE" and passage_text:
                    title = passage_text
                if passage_text:
                    text_blocks.append(passage_text)

            return {
                "doc_id": pmcid,
                "title": title,
                "source_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/",
                "license": license_str,
                "publish_date": publish_date,
                "text": "\n\n".join(text_blocks),
            }

    return None


def to_pgvector(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in values) + "]"


def ingest_manifest() -> tuple[int, int]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    document_count = 0
    chunk_count = 0

    with psycopg.connect(database_url) as connection:
        embedder = ArticleEmbedder()
        with connection.cursor() as cursor:
            with MANIFEST_PATH.open(newline="", encoding="utf-8") as csvfile:
                for row in csv.DictReader(csvfile):
                    pmcid = row["doc_id"]
                    document = fetch_bioc_document(pmcid)
                    if document is None:
                        print(f"Failed to fetch document {pmcid}")
                        time.sleep(2)
                        continue

                    cursor.execute(
                        """
                        INSERT INTO documents (id, title, source_url,
                        license, publish_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (
                            document["doc_id"],
                            document["title"],
                            document["source_url"],
                            document["license"],
                            document["publish_date"],
                        ),
                    )

                    chunks = chunk_text(
                        document["doc_id"], document["title"], document["text"]
                    )
                    vectors = embedder.embed(
                        [[chunk.title, chunk.text] for chunk in chunks]
                    )
                    for chunk, vector in zip(chunks, vectors):
                        cursor.execute(
                            """
                            INSERT INTO chunks (id, document_id, text,
                            position, embedding)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (id) DO NOTHING
                            """,
                            (
                                chunk.id,
                                chunk.document_id,
                                chunk.text,
                                chunk.position,
                                to_pgvector(vector),
                            ),
                        )

                    connection.commit()
                    document_count += 1
                    chunk_count += len(chunks)
                    time.sleep(2)

    return document_count, chunk_count


if __name__ == "__main__":
    started = time.time()
    document_count, chunk_count = ingest_manifest()
    elapsed = time.time() - started
    print(
        f"Fetched {document_count} documents and {chunk_count} chunks "
        f"in {elapsed:.2f} seconds."
    )
