"""Default RSS sources (Hindi + English) used to bootstrap the DB."""
from typing import List, Dict

DEFAULT_SOURCES: List[Dict] = [
    # --- Hindi ---
    {"name": "Dainik Jagran", "slug": "dainik-jagran",
     "url": "https://www.jagran.com/rss/news/national.xml",
     "language": "hi", "category": "general"},
    {"name": "Amar Ujala", "slug": "amar-ujala",
     "url": "https://www.amarujala.com/rss/breaking-news.xml",
     "language": "hi", "category": "general"},
    {"name": "Zee News Hindi", "slug": "zee-news-hindi",
     "url": "https://zeenews.india.com/hindi/india/rss/1.xml",
     "language": "hi", "category": "general"},
    {"name": "NDTV Hindi", "slug": "ndtv-hindi",
     "url": "https://feeds.feedburner.com/ndtvkhabar-latest",
     "language": "hi", "category": "general"},
    {"name": "Aaj Tak", "slug": "aaj-tak",
     "url": "https://www.aajtak.in/rssfeeds/?id=home",
     "language": "hi", "category": "general"},

    # --- English ---
    {"name": "BBC News", "slug": "bbc-news",
     "url": "https://feeds.bbci.co.uk/news/rss.xml",
     "language": "en", "category": "world"},
    {"name": "Reuters", "slug": "reuters",
     "url": "https://feeds.reuters.com/reuters/topNews",
     "language": "en", "category": "world"},
    {"name": "The Guardian", "slug": "the-guardian",
     "url": "https://www.theguardian.com/world/rss",
     "language": "en", "category": "world"},
    {"name": "NDTV English", "slug": "ndtv-english",
     "url": "https://feeds.feedburner.com/ndtvnews-top-stories",
     "language": "en", "category": "general"},
    {"name": "CNN", "slug": "cnn",
     "url": "http://rss.cnn.com/rss/edition.rss",
     "language": "en", "category": "world"},
]
