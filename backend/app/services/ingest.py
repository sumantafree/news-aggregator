# app/services/ingest.py

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
MAX_PER_SOURCE = 100   # 🔥 NEW (control load)


# ---------- INGEST ONE SOURCE ----------

def ingest_source(db: Session, source: Source) -> int:
    items = fetch_feed(
        source.url,
        source=source.name,          # ✅ pass source
        language=source.language
    )

    if not items:
        logger.warning("⚠️ No items for %s", source.name)
        return 0

    items = items[:MAX_PER_SOURCE]  # 🔥 LIMIT LOAD

    cutoff = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)

    # 🔥 OPTIMIZED QUERIES
    existing = db.query(
        Article.content_hash, Article.link
    ).filter(
        Article.published_at >= cutoff
    ).all()

    existing_hashes = {e[0] for e in existing}
    existing_links = {e[1] for e in existing}

    # recent titles (cross-source dedup)
    recent_titles = [
        row[0]
        for row in db.query(Article.title)
        .filter(Article.language == source.language)
        .filter(Article.published_at >= datetime.utcnow() - timedelta(hours=24))
        .limit(500)
        .all()
    ]

    new_articles: List[Article] = []
    new_count = 0

    for item in items:
        ch = content_hash(item.title, item.link)

        # ✅ FAST DEDUP
        if ch in existing_hashes or item.link in existing_links:
            continue

        # ✅ LIMITED fuzzy dedup
        if any(is_duplicate(item.title, t) for t in recent_titles[:100]):
            continue

        # 🔥 SAFE AI CALL (non-blocking failure)
        try:
            ai_sum = generate_summary(item.title, item.summary, source.language)
        except Exception as e:
            logger.warning("AI summary failed: %s", e)
            ai_sum = None

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

        new_articles.append(article)
        existing_hashes.add(ch)
        existing_links.add(item.link)
        recent_titles.append(item.title)
        new_count += 1

    # 🔥 BULK INSERT (BIG PERFORMANCE BOOST)
    if new_articles:
        db.bulk_save_objects(new_articles)
        db.commit()

    logger.info("✅ %s → %d new articles", source.name, new_count)
    return new_count


# ---------- INGEST ALL ----------

def ingest_all(db: Session) -> dict:
    sources = db.query(Source).filter(Source.is_active.is_(True)).all()

    totals = {}

    for s in sources:
        try:
            totals[s.name] = ingest_source(db, s)
        except Exception as exc:
            logger.exception("❌ Ingest failed for %s: %s", s.name, exc)
            totals[s.name] = 0

    # ---------- CLUSTER + TRENDING ----------
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

    # ---------- CACHE INVALIDATION ----------
    cache.delete_prefix("news:")
    cache.delete_prefix("trending:")
    cache.delete_prefix("sources:")

    logger.info("🚀 Ingestion complete: %s", totals)
    return totals