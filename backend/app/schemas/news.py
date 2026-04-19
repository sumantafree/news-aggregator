from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ArticleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    link: str
    summary: Optional[str] = None
    ai_summary: Optional[str] = None
    image: Optional[str] = None
    language: str
    category: Optional[str] = None
    source_name: str
    published_at: datetime
    trending_score: float = 0.0
    cluster_id: Optional[str] = None


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    url: str
    language: str
    category: Optional[str] = None
    is_active: bool


class SourceCreate(BaseModel):
    name: str
    url: str
    language: str
    category: Optional[str] = None


class SourceUpdate(BaseModel):
    is_active: Optional[bool] = None
    category: Optional[str] = None
    name: Optional[str] = None


class TrendingCluster(BaseModel):
    cluster_id: str
    language: str
    count: int
    top_title: str
    articles: List[ArticleOut]


class ClickIn(BaseModel):
    article_id: Optional[int] = None
    source_name: Optional[str] = None
    language: Optional[str] = None
    referer: Optional[str] = None


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AnalyticsOut(BaseModel):
    total_articles: int
    total_clicks: int
    articles_by_language: dict
    top_sources: list
    top_trending: list
    clicks_last_7d: list
