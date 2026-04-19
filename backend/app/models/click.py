from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.core.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=True, index=True)
    source_name = Column(String(128), nullable=True, index=True)
    language = Column(String(8), nullable=True, index=True)
    user_agent = Column(String(256), nullable=True)
    referer = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
