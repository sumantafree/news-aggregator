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

# 🔥 MASTER FEED CONFIG (UPDATED)
FEEDS: List[Dict] = [
    # 🇮🇳 ENGLISH NEWS
    {"url": "http://feeds.bbci.co.uk/news/rss.xml", "source": "BBC", "lang": "en"},
    {"url": "https://indianexpress.com/feed/", "source": "Indian Express", "lang": "en"},
    {"url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV", "lang": "en"},
    {"url": "https://www.hindustantimes.com/feeds/rss/topnews/rssfeed.xml", "source": "HT", "lang": "en"},
    {"url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "source": "TOI", "lang": "en"},

    # 🇮🇳 HINDI NEWS
    {"url": "https://www.amarujala.com/rss/breaking-news.xml", "source": "Amar Ujala", "lang": "hi"},
    {"url": "https://feeds.feedburner.com/ndtvkhabar-latest", "source": "NDTV Hindi", "lang": "hi"},
    {"url": "https://www.aajtak.in/rssfeeds/?id=home", "source": "AajTak", "lang": "hi"},

    # ❌ REMOVED BROKEN:
    # Jagran (404)
    # Zee (bad redirects / no entries)
]


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
    # media
    for key in ("media_content", "media_thumbnail"):
        val = entry.get(key)
        if isinstance(val, list) and val:
            return val[0].get("url")

    # enclosure
    for link in entry.get("links", []):
        if link.get("rel") == "enclosure":
            return link.get("href")

    # HTML fallback
    html = entry.get("summary", "")
    match = re.search(r'<img[^>]+src=["\']([^"\']+)', html)
    return match.group(1) if match else None


# ---------- CORE FETCH ----------

def fetch_single_feed(feed: Dict) -> List[FeedItem]:
    url = feed["url"]
    source = feed["source"]
    lang = feed["lang"]

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


# ---------- AGGREGATOR ----------

def fetch_all_feeds() -> List[FeedItem]:
    """Fetch all feeds with deduplication"""
    all_items: List[FeedItem] = []
    seen_links = set()

    for feed in FEEDS:
        items = fetch_single_feed(feed)

        for item in items:
            if item.link in seen_links:
                continue
            seen_links.add(item.link)
            all_items.append(item)

    # Sort latest first
    all_items.sort(key=lambda x: x.published, reverse=True)

    logger.info("TOTAL news collected: %d", len(all_items))
    return all_items