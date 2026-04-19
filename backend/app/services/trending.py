"""Trending score: recency × cluster frequency."""
from __future__ import annotations

import math
from collections import Counter
from datetime import datetime
from typing import Iterable, List

from app.models.article import Article


def compute_trending_scores(articles: List[Article]) -> None:
    """In-place update article.trending_score based on cluster frequency + recency."""
    now = datetime.utcnow()
    cluster_counts: Counter = Counter(a.cluster_id for a in articles if a.cluster_id)

    for a in articles:
        freq = cluster_counts.get(a.cluster_id, 1) if a.cluster_id else 1
        # Age in hours
        age_h = max((now - a.published_at).total_seconds() / 3600.0, 0.25)
        # Half-life ~18h
        recency = math.exp(-age_h / 18.0)
        a.trending_score = float(freq) * recency


def top_clusters(articles: Iterable[Article], language: str, limit: int = 10):
    """Return [(cluster_id, count, top_article)] ordered by score."""
    by_cluster: dict[str, list[Article]] = {}
    for a in articles:
        if a.language != language or not a.cluster_id:
            continue
        by_cluster.setdefault(a.cluster_id, []).append(a)

    out = []
    for cid, items in by_cluster.items():
        items.sort(key=lambda x: x.trending_score, reverse=True)
        score = sum(x.trending_score for x in items)
        out.append((cid, len(items), items[0], score, items))
    out.sort(key=lambda x: x[3], reverse=True)
    return out[:limit]
