"""Fuzzy deduplication + lightweight clustering by title similarity."""
from __future__ import annotations

from typing import Iterable, List, Tuple
import hashlib

from rapidfuzz import fuzz

from app.services.text_utils import normalize_title

DEDUP_THRESHOLD = 85
CLUSTER_THRESHOLD = 75


def is_duplicate(title_a: str, title_b: str, threshold: int = DEDUP_THRESHOLD) -> bool:
    if not title_a or not title_b:
        return False
    a = normalize_title(title_a)
    b = normalize_title(title_b)
    if not a or not b:
        return False
    return fuzz.token_set_ratio(a, b) >= threshold


def cluster_titles(
    items: List[Tuple[int, str]], threshold: int = CLUSTER_THRESHOLD
) -> dict[int, str]:
    """Cluster (id, title) pairs → {id: cluster_id}. O(n^2) but fine for <10k."""
    clusters: dict[int, str] = {}
    centroids: List[Tuple[str, str]] = []  # (cluster_id, normalized_title)

    for item_id, title in items:
        norm = normalize_title(title)
        if not norm:
            continue
        assigned = None
        for cid, centroid in centroids:
            if fuzz.token_set_ratio(norm, centroid) >= threshold:
                assigned = cid
                break
        if assigned is None:
            assigned = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:16]
            centroids.append((assigned, norm))
        clusters[item_id] = assigned
    return clusters


def dedup_batch(incoming: Iterable[dict], existing_titles: List[str]) -> List[dict]:
    """Drop incoming items whose title is a fuzzy match of any existing title."""
    out: List[dict] = []
    seen_titles: List[str] = list(existing_titles)
    for item in incoming:
        title = item.get("title", "")
        if any(is_duplicate(title, t) for t in seen_titles):
            continue
        out.append(item)
        seen_titles.append(title)
    return out
