import math
import re
from collections import Counter
from itertools import pairwise

from app.rag.chunking import Chunk


def tokens(s: str):
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+", s.lower())


def lexical_score(query: str, text: str) -> float:
    q = Counter(tokens(query))
    d = Counter(tokens(text))
    if not q or not d:
        return 0.0
    return sum(min(v, d[k]) for k, v in q.items()) / max(1, sum(q.values()))


def dense_score(query: str, text: str) -> float:
    # Deterministic local semantic-ish fallback based on hashed token trigrams.
    def vec(s):
        c = Counter()
        ts = tokens(s)
        for t in ts:
            c[hash(t) % 257] += 1
        for a, b in pairwise(ts):
            c[hash(a + "::" + b) % 257] += 0.5
        return c

    a, b = vec(query), vec(text)
    dot = sum(v * b[k] for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0) + (1 / (k + rank))
    return scores


def hybrid_retrieve(query: str, chunks: list[Chunk], top_k: int = 8):
    lex = sorted(
        chunks,
        key=lambda c: lexical_score(query, c.text),
        reverse=True,
    )

    dense = sorted(
        chunks,
        key=lambda c: dense_score(query, c.text),
        reverse=True,
    )

    fused = reciprocal_rank_fusion(
        [
            [c.id for c in lex[:30]],
            [c.id for c in dense[:30]],
        ]
    )

    by_id = {c.id: c for c in chunks}

    return [
        (by_id[i], s)
        for i, s in sorted(
            fused.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]
    ]


class Reranker:
    def rerank(self, query, items):
        # Configurable deterministic reranker; replace with cross-encoder in production.
        return sorted(
            items,
            key=lambda x: (
                lexical_score(query, x[0].text) * 0.7 + dense_score(query, x[0].text) * 0.3
            ),
            reverse=True,
        )
