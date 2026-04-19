"""Fault-tolerant RSS fetching + normalization."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import feedparser
import httpx

from app.services.text_utils import short_summary, strip_html

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (compatible; NewsAggregatorBot/1.0; +https://example.com/bot)"
)


@dataclass
class FeedItem:
    title: str
    link: str
    summary: str
    image: Optional[str]
    published: datetime


def _parse_date(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed", "created_parsed"):
        val = entry.get(key)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc).replace(tzinfo=None)
            except Exception:
                continue
    return datetime.utcnow()


def _extract_image(entry) -> Optional[str]:
    # media:content / media:thumbnail
    for key in ("media_content", "media_thumbnail"):
        val = entry.get(key)
        if val and isinstance(val, list) and val:
            url = val[0].get("url")
            if url:
                return url
    # enclosure
    links = entry.get("links") or []
    for l in links:
        if l.get("rel") == "enclosure" and (l.get("type") or "").startswith("image"):
            return l.get("href")
    # fallback: first <img> in summary/content
    html = entry.get("summary") or ""
    if "<img" in html:
        import re
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        if m:
            return m.group(1)
    return None


def fetch_feed(url: str, timeout: float = 10.0) -> List[FeedItem]:
    """Fetch & parse a single RSS feed. Returns [] on failure (never raises)."""
    try:
        with httpx.Client(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, */*"},
            follow_redirects=True,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            content = resp.content
    except Exception as exc:
        logger.warning("RSS fetch failed %s: %s", url, exc)
        return []

    try:
        parsed = feedparser.parse(content)
    except Exception as exc:
        logger.warning("RSS parse failed %s: %s", url, exc)
        return []

    items: List[FeedItem] = []
    for entry in parsed.entries or []:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title or not link:
            continue
        raw_summary = entry.get("summary") or entry.get("description") or ""
        summary = short_summary(strip_html(raw_summary), 300)
        items.append(
            FeedItem(
                title=title,
                link=link,
                summary=summary,
                image=_extract_image(entry),
                published=_parse_date(entry),
            )
        )
    return items
