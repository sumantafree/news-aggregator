# app/services/rss_fetcher.py

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Dict

import feedparser
import httpx

from app.services.text_utils import short_summary, strip_html

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (NewsAggregatorBot/2.0)"


@dataclass
class FeedItem:
    title: str
    link: str
    summary: str
    image: Optional[str]
    published: datetime
    source: str
    language: str


# ---------- HELPERS ----------

def _parse_date(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        val = entry.get(key)
        if val:
            try:
                return datetime(*val[:6], tzinfo=timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
    return datetime.utcnow()


def _extract_image(entry) -> Optional[str]:
    for key in ("media_content", "media_thumbnail"):
        val = entry.get(key)
        if isinstance(val, list) and val:
            return val[0].get("url")

    for link in entry.get("links", []):
        if link.get("rel") == "enclosure":
            return link.get("href")

    html = entry.get("summary", "")
    match = re.search(r'<img[^>]+src=["\']([^"\']+)', html)
    return match.group(1) if match else None


# ---------- CORE ----------

def fetch_single_feed(feed: Dict) -> List[FeedItem]:
    url = feed["url"]
    source = feed.get("source", "Unknown")
    lang = feed.get("lang", "en")

    try:
        with httpx.Client(
            timeout=10,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            resp = client.get(url)
            logger.info("Fetch %s → %s", source, resp.status_code)
            resp.raise_for_status()

    except Exception as e:
        logger.warning("FAILED %s: %s", source, e)
        return []

    parsed = feedparser.parse(resp.content)

    if parsed.bozo:
        logger.warning("Malformed feed %s", source)

    if not parsed.entries:
        logger.warning("EMPTY feed %s", source)
        return []

    items: List[FeedItem] = []

    for entry in parsed.entries:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()

        if not title or not link:
            continue

        raw = (
            entry.get("summary")
            or entry.get("description")
            or entry.get("content", [{}])[0].get("value", "")
        )

        summary = short_summary(strip_html(raw), 280)

        items.append(
            FeedItem(
                title=title,
                link=link,
                summary=summary,
                image=_extract_image(entry),
                published=_parse_date(entry),
                source=source,
                language=lang,
            )
        )

    logger.info("Parsed %d items from %s", len(items), source)
    return items


# ---------- BACKWARD COMPATIBILITY ----------

def fetch_feed(url: str, source: str = "", language: str = "en") -> List[FeedItem]:
    """Compatibility wrapper for old ingestion code"""
    return fetch_single_feed({
        "url": url,
        "source": source or "Unknown",
        "lang": language,
    })