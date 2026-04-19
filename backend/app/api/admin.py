from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.core.database import SessionLocal, get_db
from app.core.security import (
    create_access_token,
    get_current_admin,
    verify_password,
)
from app.models.admin import AdminUser
from app.models.article import Article
from app.models.click import Click
from app.models.source import Source
from app.schemas.news import (
    AnalyticsOut,
    LoginIn,
    SourceCreate,
    SourceOut,
    SourceUpdate,
    TokenOut,
)
from app.services.ingest import ingest_all
from app.services.text_utils import slugify

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(subject=user.username)
    return TokenOut(access_token=token)


@router.get("/sources", response_model=List[SourceOut])
def admin_list_sources(
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(Source).order_by(Source.name.asc()).all()


@router.post("/source", response_model=SourceOut, status_code=201)
def add_source(
    payload: SourceCreate,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if payload.language not in {"hi", "en"}:
        raise HTTPException(400, "language must be 'hi' or 'en'")
    slug = slugify(payload.name)
    if db.query(Source).filter(
        (Source.slug == slug) | (Source.url == payload.url) | (Source.name == payload.name)
    ).first():
        raise HTTPException(409, "Source already exists")
    src = Source(
        name=payload.name,
        slug=slug,
        url=payload.url,
        language=payload.language,
        category=payload.category,
        is_active=True,
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    cache.delete_prefix("sources:")
    return src


@router.patch("/source/{source_id}", response_model=SourceOut)
def update_source(
    source_id: int,
    payload: SourceUpdate,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    src = db.query(Source).filter(Source.id == source_id).first()
    if not src:
        raise HTTPException(404, "Source not found")
    if payload.is_active is not None:
        src.is_active = payload.is_active
    if payload.category is not None:
        src.category = payload.category
    if payload.name is not None:
        src.name = payload.name
        src.slug = slugify(payload.name)
    db.commit()
    db.refresh(src)
    cache.delete_prefix("sources:")
    cache.delete_prefix("news:")
    return src


@router.delete("/source/{source_id}", status_code=204)
def delete_source(
    source_id: int,
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    src = db.query(Source).filter(Source.id == source_id).first()
    if not src:
        raise HTTPException(404, "Source not found")
    db.delete(src)
    db.commit()
    cache.delete_prefix("sources:")
    cache.delete_prefix("news:")
    return None


def _run_ingest():
    db = SessionLocal()
    try:
        ingest_all(db)
    finally:
        db.close()


@router.post("/refresh")
def manual_refresh(
    background: BackgroundTasks,
    _: str = Depends(get_current_admin),
):
    background.add_task(_run_ingest)
    return {"ok": True, "message": "Ingest started"}


@router.get("/analytics", response_model=AnalyticsOut)
def analytics(
    _: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_articles = db.query(func.count(Article.id)).scalar() or 0
    total_clicks = db.query(func.count(Click.id)).scalar() or 0

    lang_rows = (
        db.query(Article.language, func.count(Article.id)).group_by(Article.language).all()
    )
    by_lang = {lang: count for lang, count in lang_rows}

    top_sources_rows = (
        db.query(Click.source_name, func.count(Click.id).label("c"))
        .group_by(Click.source_name)
        .order_by(func.count(Click.id).desc())
        .limit(10)
        .all()
    )
    top_sources = [{"source": r[0], "clicks": int(r[1])} for r in top_sources_rows if r[0]]

    top_trending_rows = (
        db.query(Article.cluster_id, Article.title, Article.language)
        .filter(Article.cluster_id.isnot(None))
        .order_by(Article.trending_score.desc())
        .limit(10)
        .all()
    )
    top_trending = [
        {"cluster_id": r[0], "title": r[1], "language": r[2]} for r in top_trending_rows
    ]

    since = datetime.utcnow() - timedelta(days=7)
    per_day_rows = (
        db.query(func.date(Click.created_at), func.count(Click.id))
        .filter(Click.created_at >= since)
        .group_by(func.date(Click.created_at))
        .order_by(func.date(Click.created_at))
        .all()
    )
    clicks_last_7d = [{"date": str(d), "clicks": int(c)} for d, c in per_day_rows]

    return AnalyticsOut(
        total_articles=int(total_articles),
        total_clicks=int(total_clicks),
        articles_by_language=by_lang,
        top_sources=top_sources,
        top_trending=top_trending,
        clicks_last_7d=clicks_last_7d,
    )
