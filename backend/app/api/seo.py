"""Sitemap + robots.txt served directly by the backend.

The frontend proxies these so both work regardless of deployment topology.
"""
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.article import Article
from app.models.source import Source

router = APIRouter(tags=["seo"])


def _url_entry(loc: str, lastmod: str | None = None, priority: str = "0.7") -> str:
    lm = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
    return (
        "<url>"
        f"<loc>{escape(loc)}</loc>"
        f"{lm}"
        f"<changefreq>hourly</changefreq>"
        f"<priority>{priority}</priority>"
        "</url>"
    )


@router.get("/sitemap.xml", include_in_schema=False)
def sitemap(db: Session = Depends(get_db)):
    base = settings.SITE_URL.rstrip("/")
    entries = [
        _url_entry(f"{base}/", priority="1.0"),
        _url_entry(f"{base}/hi", priority="0.9"),
        _url_entry(f"{base}/en", priority="0.9"),
    ]

    # Sources
    for s in db.query(Source).filter(Source.is_active.is_(True)).all():
        entries.append(_url_entry(f"{base}/{s.language}/source/{s.slug}", priority="0.6"))

    # Recent articles (last 48h)
    since = datetime.utcnow() - timedelta(hours=48)
    articles = (
        db.query(Article)
        .filter(Article.published_at >= since)
        .order_by(Article.published_at.desc())
        .limit(5000)
        .all()
    )
    for a in articles:
        loc = f"{base}/{a.language}/article/{a.id}/{a.slug}"
        entries.append(_url_entry(loc, lastmod=a.published_at.strftime("%Y-%m-%d"), priority="0.8"))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(entries)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/robots.txt", include_in_schema=False)
def robots():
    base = settings.SITE_URL.rstrip("/")
    txt = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    return Response(content=txt, media_type="text/plain")
