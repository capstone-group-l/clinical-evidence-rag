import re

from app.schemas import Chunk, RetrievedPassage
from rank_bm25 import BM25Okapi

TOKEN = re.compile(r"\w+(?:[-./']\w+)*")


def acronym(word: str) -> str | None:
    # Two or more capitals marks an acronym
    word = word.removesuffix("'s")
    if sum(c.isupper() for c in word) < 2:
        return None
    # Drop a plural "s" after a capital or digit
    if word.endswith("s") and (word[-2].isupper() or word[-2].isdigit()):
        word = word[:-1]
    return word


# Takes a string of text and returns a list of tokens
def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in TOKEN.findall(text):
        tok = raw.lower()
        tokens.append(tok)
        if tok.endswith("'s"):
            tokens.append(tok[:-2])
        words = [raw]
        parts = re.split(r"[-/]", raw)
        if len(parts) > 1:
            tokens.extend(part.lower() for part in parts)
            words.extend(parts)
        for word in words:
            found = acronym(word)
            if found:
                tokens.append(found)
    return tokens


class BM25Retriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.build(chunks)

    # Builds a BM25 index from a list of chunks
    def build(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        corpus = [tokenize(chunk.text) for chunk in chunks]
        self.index = BM25Okapi(corpus) if corpus else None

    # Retrieves the passages most relevant to a question
    def retrieve(self, question: str, k: int = 5) -> list[RetrievedPassage]:
        query = tokenize(question)
        if not query or self.index is None:
            return []

        scores = self.index.get_scores(query)
        pairs = list(enumerate(scores))
        pairs.sort(key=lambda pair: pair[1], reverse=True)

        results = []
        for position, score in pairs[:k]:
            if score > 0:
                results.append(
                    RetrievedPassage(
                        chunk=self.chunks[position], score=float(score)
                    )
                )
        return results
