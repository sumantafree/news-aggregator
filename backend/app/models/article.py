from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Index,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    slug = Column(String(600), nullable=False, index=True)
    link = Column(String(1024), nullable=False, unique=True, index=True)
    summary = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    image = Column(String(1024), nullable=True)
    language = Column(String(8), nullable=False, index=True)
    category = Column(String(64), nullable=True, index=True)

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    source_name = Column(String(128), nullable=False)

    published_at = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cluster_id = Column(String(64), nullable=True, index=True)
    trending_score = Column(Float, default=0.0)
    content_hash = Column(String(64), nullable=True, index=True)

    source = relationship("Source")


Index("ix_articles_lang_pub", Article.language, Article.published_at.desc())
