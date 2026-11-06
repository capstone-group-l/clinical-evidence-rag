import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

import psycopg

logger = logging.getLogger(__name__)

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "can",
    "does",
    "for",
    "from",
    "how",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "which",
    "with",
}
UMLS_RELEASE = "2026AB"


def extract_terms(question: str, limit: int = 20) -> list[str]:
    words = [word.lower() for word in WORD.findall(question)]
    terms: list[str] = []
    for size in (3, 2, 1):
        for start in range(len(words) - size + 1):
            part = words[start : start + size]
            if any(word in STOP_WORDS for word in part):
                continue
            term = " ".join(part)
            if term not in terms:
                terms.append(term)
            if len(terms) >= limit:
                return terms
    return terms


class UMLSQueryExpander:
    def __init__(
        self,
        database_url,
        api_key,
        release=None,
        timeout=5,
    ):
        self.database_url = database_url
        self.api_key = api_key
        self.timeout = timeout
        self.release = release or self.check_release()

    def check_release(self) -> str:
        if not self.api_key:
            return UMLS_RELEASE

        params = urllib.parse.urlencode(
            {"string": "medical", "apiKey": self.api_key}
        )
        url = f"https://uts-ws.nlm.nih.gov/rest/search/{UMLS_RELEASE}?{params}"
        try:
            request = urllib.request.Request(url)
            with urllib.request.urlopen(
                request, timeout=self.timeout
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, ValueError) as error:
            logger.warning(
                "Could not resolve the current UMLS release: %s; "
                "falling back to UMLS release: %r",
                error,
                UMLS_RELEASE,
            )
            return UMLS_RELEASE

        result = payload.get("result", {})
        results = result.get("results", []) if isinstance(result, dict) else []
        for item in results:
            if isinstance(item, dict):
                match = re.search(r"/content/([^/]+)/", item.get("uri", ""))
                if match:
                    return match.group(1)

        logger.warning("UMLS release unavailable; using %r", UMLS_RELEASE)
        return UMLS_RELEASE

    def expand(self, question: str) -> list[str]:
        expanded = []
        terms = extract_terms(question)
        original_terms = set(terms)
        for term in terms:
            synonyms = self.check_cache(term)
            for synonym in synonyms:
                if (
                    synonym.lower() not in original_terms
                    and synonym not in expanded
                ):
                    expanded.append(synonym)
        return expanded

    def check_cache(self, term: str) -> list[str]:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                """
                SELECT synonyms FROM umls_term_cache
                WHERE term = %s AND umls_release = %s
                """,
                (term, self.release),
            ).fetchone()
            if row is not None:
                return list(row[0])

        synonyms = self.lookup(term)
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO umls_term_cache
                    (term, synonyms, umls_release, looked_up_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (term, umls_release) DO NOTHING
                """,
                (term, synonyms, self.release, date.today()),
            )
        return synonyms

    def lookup(self, term: str) -> list[str]:
        if not self.api_key:
            return []
        params = urllib.parse.urlencode(
            {
                "string": term,
                "apiKey": self.api_key,
                "returnIdType": "concept",
                "searchType": "words",
                "sabs": "MSH",
            }
        )
        url = f"https://uts-ws.nlm.nih.gov/rest/search/{self.release}?{params}"
        try:
            request = urllib.request.Request(url)
            with urllib.request.urlopen(
                request, timeout=self.timeout
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, ValueError) as error:
            logger.warning("UMLS lookup stalled for term %r: %s", term, error)
            return []

        result: Any = payload.get("result", {})
        if not isinstance(result, dict):
            return []
        results = result.get("results", [])
        if not isinstance(results, list):
            return []
        names = []
        for item in results:
            if isinstance(item, dict) and item.get("name"):
                names.append(item["name"])
        return list(dict.fromkeys(names))
