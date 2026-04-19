"""Ingest pipeline: fetch feeds → normalize → dedup → cluster → persist."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.cache import cache
from app.models.article import Article
from app.models.source import Source
from app.services.dedup import cluster_titles, is_duplicate
from app.services.rss_fetcher import fetch_feed
from app.services.summarizer import generate_summary
from app.services.text_utils import content_hash, slugify
from app.services.trending import compute_trending_scores

logger = logging.getLogger(__name__)

LOOKBACK_DAYS = 3
MAX_PER_LANG = 500


def ingest_source(db: Session, source: Source) -> int:
    items = fetch_feed(source.url)
    if not items:
        logger.info("No items for %s", source.name)
        return 0

    existing_hashes = {
        row[0]
        for row in db.query(Article.content_hash)
        .filter(Article.source_id == source.id)
        .filter(Article.published_at >= datetime.utcnow() - timedelta(days=LOOKBACK_DAYS))
        .all()
    }
    existing_links = {
        row[0]
        for row in db.query(Article.link)
        .filter(Article.source_id == source.id)
        .filter(Article.published_at >= datetime.utcnow() - timedelta(days=LOOKBACK_DAYS))
        .all()
    }
    # also pull recent titles across all sources for cross-source dedup
    recent_titles = [
        row[0]
        for row in db.query(Article.title)
        .filter(Article.language == source.language)
        .filter(Article.published_at >= datetime.utcnow() - timedelta(days=1))
        .limit(1000)
        .all()
    ]

    new_count = 0
    for item in items:
        ch = content_hash(item.title, item.link)
        if ch in existing_hashes or item.link in existing_links:
            continue
        # cross-source fuzzy dedup (only for very recent items)
        if any(is_duplicate(item.title, t) for t in recent_titles[:300]):
            continue

        ai_sum = generate_summary(item.title, item.summary, source.language)
        article = Article(
            title=item.title[:500],
            slug=slugify(item.title),
            link=item.link,
            summary=item.summary,
            ai_summary=ai_sum,
            image=item.image,
            language=source.language,
            category=source.category,
            source_id=source.id,
            source_name=source.name,
            published_at=item.published,
            content_hash=ch,
        )
        db.add(article)
        existing_hashes.add(ch)
        existing_links.add(item.link)
        recent_titles.append(item.title)
        new_count += 1

    db.commit()
    return new_count


def ingest_all(db: Session) -> dict:
    """Fetch every active source and update clusters + trending."""
    sources = db.query(Source).filter(Source.is_active.is_(True)).all()
    totals: dict = {}
    for s in sources:
        try:
            totals[s.name] = ingest_source(db, s)
        except Exception as exc:
            logger.exception("Ingest failed for %s: %s", s.name, exc)
            totals[s.name] = 0

    # Re-cluster recent articles per language
    for lang in ("hi", "en"):
        recent = (
            db.query(Article)
            .filter(Article.language == lang)
            .filter(Article.published_at >= datetime.utcnow() - timedelta(days=2))
            .order_by(Article.published_at.desc())
            .limit(MAX_PER_LANG)
            .all()
        )
        clusters = cluster_titles([(a.id, a.title) for a in recent])
        for a in recent:
            a.cluster_id = clusters.get(a.id)
        compute_trending_scores(recent)
    db.commit()

    # invalidate caches
    cache.delete_prefix("news:")
    cache.delete_prefix("trending:")
    cache.delete_prefix("sources:")
    return totals
