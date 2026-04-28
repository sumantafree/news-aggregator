from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.core.database import get_db
from app.core.limiter import limiter
from app.models.article import Article
from app.models.source import Source
from app.schemas.news import ArticleOut, SourceOut, TrendingCluster
from app.services.trending import top_clusters

router = APIRouter(tags=["news"])

# ---------------- NEWS ---------------- #

@router.get("/news")
@limiter.limit("60/minute")
def list_news(
    request: Request,
    lang: str = Query("all", pattern="^(hi|en|all)$"),
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    cache_key = f"news:{lang}:{source}:{category}:{limit}:{offset}"
    cached = cache.get_json(cache_key)
    if cached:
        return cached

    q = db.query(Article)

    # ✅ FILTER FIRST (important for index usage)
    if lang != "all":
        q = q.filter(Article.language == lang)

    if category:
        q = q.filter(Article.category == category)

    if source:
        q = q.join(Source).filter(Source.slug == source)

    # ✅ TIME FILTER LAST
    q = q.filter(
        Article.published_at >= datetime.utcnow() - timedelta(days=7)
    )

    total = q.count()

    items = (
        q.order_by(desc(Article.published_at))
        .offset(offset)
        .limit(limit)
        .all()
    )

    data = [ArticleOut.from_orm(a).dict() for a in items]

    response = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": data,
    }

    cache.set_json(cache_key, response, ttl=120)
    return response


# ---------------- SOURCES ---------------- #

@router.get("/sources")
@limiter.limit("60/minute")
def list_sources(
    request: Request,
    lang: Optional[str] = Query(None, pattern="^(hi|en)$"),
    db: Session = Depends(get_db),
):
    cache_key = f"sources:{lang or 'all'}"
    cached = cache.get_json(cache_key)
    if cached:
        return cached

    q = db.query(Source).filter(Source.is_active.is_(True))

    if lang:
        q = q.filter(Source.language == lang)

    items = q.order_by(Source.name.asc()).all()

    data = [SourceOut.from_orm(s).dict() for s in items]

    cache.set_json(cache_key, data, ttl=600)
    return data


# ---------------- TRENDING ---------------- #

@router.get("/trending")
@limiter.limit("60/minute")
def trending(
    request: Request,
    lang: str = Query("en", pattern="^(hi|en)$"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    cache_key = f"trending:{lang}:{limit}"
    cached = cache.get_json(cache_key)
    if cached:
        return cached

    cutoff = datetime.utcnow() - timedelta(days=2)

    recent = (
        db.query(Article)
        .filter(Article.language == lang)
        .filter(Article.published_at >= cutoff)
        .order_by(desc(Article.trending_score))
        .limit(300)
        .all()
    )

    clusters = top_clusters(recent, language=lang, limit=limit)

    data = [
        {
            "cluster_id": cid,
            "language": lang,
            "count": count,
            "top_title": top.title,
            "articles": [ArticleOut.from_orm(a).dict() for a in items[:5]],
        }
        for cid, count, top, _, items in clusters
    ]

    cache.set_json(cache_key, data, ttl=300)
    return data


# ---------------- CATEGORIES ---------------- #

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Article.category).filter(
        Article.category.isnot(None)
    ).distinct().all()

    return sorted({r[0] for r in rows if r[0]})