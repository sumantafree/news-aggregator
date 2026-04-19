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

VALID_LANGS = {"hi", "en", "all"}


@router.get("/news", response_model=List[ArticleOut])
@limiter.limit("60/minute")
def list_news(
    request: Request,
    lang: str = Query("all", pattern="^(hi|en|all)$"),
    source: Optional[str] = Query(None, description="Source slug"),
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    cache_key = f"news:{lang}:{source}:{category}:{limit}:{offset}"
    cached = cache.get_json(cache_key)
    if cached is not None:
        return cached

    q = db.query(Article).filter(
        Article.published_at >= datetime.utcnow() - timedelta(days=7)
    )
    if lang != "all":
        q = q.filter(Article.language == lang)
    if source:
        src = db.query(Source).filter(Source.slug == source).first()
        if src:
            q = q.filter(Article.source_id == src.id)
        else:
            return []
    if category:
        q = q.filter(Article.category == category)

    items = q.order_by(desc(Article.published_at)).offset(offset).limit(limit).all()
    data = [ArticleOut.model_validate(a).model_dump() for a in items]
    cache.set_json(cache_key, data)
    return data


@router.get("/sources", response_model=List[SourceOut])
@limiter.limit("60/minute")
def list_sources(
    request: Request,
    lang: Optional[str] = Query(None, pattern="^(hi|en)$"),
    db: Session = Depends(get_db),
):
    cache_key = f"sources:{lang or 'all'}"
    cached = cache.get_json(cache_key)
    if cached is not None:
        return cached

    q = db.query(Source).filter(Source.is_active.is_(True))
    if lang:
        q = q.filter(Source.language == lang)
    items = q.order_by(Source.name.asc()).all()
    data = [SourceOut.model_validate(s).model_dump() for s in items]
    cache.set_json(cache_key, data)
    return data


@router.get("/trending", response_model=List[TrendingCluster])
@limiter.limit("60/minute")
def trending(
    request: Request,
    lang: str = Query("en", pattern="^(hi|en)$"),
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db),
):
    cache_key = f"trending:{lang}:{limit}"
    cached = cache.get_json(cache_key)
    if cached is not None:
        return cached

    recent = (
        db.query(Article)
        .filter(Article.language == lang)
        .filter(Article.published_at >= datetime.utcnow() - timedelta(days=2))
        .order_by(desc(Article.trending_score))
        .limit(500)
        .all()
    )
    clusters = top_clusters(recent, language=lang, limit=limit)
    data = []
    for cid, count, top, _score, items in clusters:
        data.append(
            TrendingCluster(
                cluster_id=cid,
                language=lang,
                count=count,
                top_title=top.title,
                articles=[ArticleOut.model_validate(a) for a in items[:5]],
            ).model_dump()
        )
    cache.set_json(cache_key, data, ttl=300)
    return data


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Article.category).filter(Article.category.isnot(None)).distinct().all()
    return sorted({r[0] for r in rows if r[0]})
