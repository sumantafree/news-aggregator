from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    slug = Column(String(128), nullable=False, unique=True, index=True)
    url = Column(String(512), nullable=False)  # RSS feed URL
    language = Column(String(8), nullable=False, index=True)  # "hi" | "en"
    category = Column(String(64), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
