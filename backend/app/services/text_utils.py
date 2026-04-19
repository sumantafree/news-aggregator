"""Small text utilities used across services."""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup


_STOPWORDS_EN = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "by",
    "with", "is", "are", "was", "were", "as", "at", "be", "from", "that",
    "this", "it", "its", "has", "have", "had", "will", "but", "not", "they",
}

_STOPWORDS_HI = {
    "और", "का", "की", "के", "है", "हैं", "में", "से", "को", "पर", "यह",
    "वह", "कि", "भी", "था", "थे", "थी", "होगा", "होगी", "हो", "गया", "गई",
    "ने", "एक", "लिए", "अब", "तक",
}


def slugify(text: str, max_len: int = 90) -> str:
    text = text or ""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text.lower()[:max_len] or "article"


def strip_html(html: Optional[str]) -> str:
    if not html:
        return ""
    try:
        return BeautifulSoup(html, "lxml").get_text(" ", strip=True)
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


def content_hash(title: str, link: str) -> str:
    key = (title or "").lower().strip() + "|" + (link or "").lower().strip()
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def normalize_title(title: str) -> str:
    t = (title or "").lower()
    t = re.sub(r"[^\w\s\u0900-\u097F]", " ", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def keywords(title: str, language: str, top: int = 6) -> list[str]:
    stop = _STOPWORDS_HI if language == "hi" else _STOPWORDS_EN
    tokens = [w for w in normalize_title(title).split() if len(w) > 2 and w not in stop]
    # preserve order, unique
    seen = set()
    out: list[str] = []
    for w in tokens:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out[:top]


def short_summary(text: str, max_chars: int = 220) -> str:
    text = strip_html(text).strip()
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    cut = text[:max_chars]
    # try to break at last sentence boundary
    for sep in [". ", "। ", "! ", "? "]:
        idx = cut.rfind(sep)
        if idx > 80:
            return cut[: idx + 1].strip()
    return cut.rsplit(" ", 1)[0] + "…"
