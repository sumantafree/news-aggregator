"""Lightweight extractive AI summary (Hindi + English).

We deliberately avoid external LLM dependencies: sources only give us
RSS titles + short descriptions, so an extractive approach is enough
and keeps the system deployable without API keys.
"""
from __future__ import annotations

import re
from typing import List

from app.services.text_utils import strip_html, keywords


def _split_sentences(text: str) -> List[str]:
    # Split on Devanagari danda '।' and English punctuation.
    parts = re.split(r"(?<=[.!?।])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _score_sentence(sentence: str, kw: List[str]) -> float:
    low = sentence.lower()
    hits = sum(1 for k in kw if k in low)
    length_bonus = min(len(sentence), 160) / 160.0
    return hits + length_bonus * 0.5


def generate_summary(title: str, description: str, language: str, max_chars: int = 240) -> str:
    """Extractive 1–2 sentence summary."""
    text = strip_html(description or "").strip()
    if not text:
        return title
    sents = _split_sentences(text)
    if not sents:
        return text[:max_chars].rstrip() + ("…" if len(text) > max_chars else "")

    kw = keywords(title, language)
    scored = [(s, _score_sentence(s, kw)) for s in sents]
    scored.sort(key=lambda x: x[1], reverse=True)

    out = ""
    for s, _ in scored:
        if len(out) + len(s) + 1 > max_chars:
            break
        out = (out + " " + s).strip()
    if not out:
        out = sents[0]
    return out[:max_chars].rstrip() + ("…" if len(out) > max_chars else "")
