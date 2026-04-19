"""DB schema creation + default data seeding."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.core.config import settings
from app.models.admin import AdminUser
from app.models.source import Source
from app.services.seed_sources import DEFAULT_SOURCES

# Import models so their tables are registered
from app import models  # noqa: F401

logger = logging.getLogger(__name__)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_admin(db: Session) -> None:
    if db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first():
        return
    user = AdminUser(
        username=settings.ADMIN_USERNAME,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(user)
    db.commit()
    logger.info("Seeded admin user: %s", settings.ADMIN_USERNAME)


def seed_sources(db: Session) -> None:
    if db.query(Source).count() > 0:
        return
    for s in DEFAULT_SOURCES:
        db.add(Source(**s, is_active=True))
    db.commit()
    logger.info("Seeded %d default sources", len(DEFAULT_SOURCES))


def run_bootstrap() -> None:
    create_tables()
    db = SessionLocal()
    try:
        seed_admin(db)
        seed_sources(db)
    finally:
        db.close()
