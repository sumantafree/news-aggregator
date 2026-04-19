"""Celery app + periodic RSS refresh."""
from __future__ import annotations

import logging

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.ingest import ingest_all

logger = logging.getLogger(__name__)

broker_url = settings.REDIS_URL or "memory://"
result_backend = settings.REDIS_URL or "cache+memory://"

celery_app = Celery(
    "news_aggregator",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="tasks.refresh_feeds")
def refresh_feeds() -> dict:
    db = SessionLocal()
    try:
        totals = ingest_all(db)
        logger.info("Feed refresh done: %s", totals)
        return totals
    finally:
        db.close()


# Periodic schedule — every N seconds as configured
celery_app.conf.beat_schedule = {
    "refresh-feeds": {
        "task": "tasks.refresh_feeds",
        "schedule": float(settings.RSS_REFRESH_INTERVAL),
    },
    # Daily cleanup could live here too
    "daily-compute": {
        "task": "tasks.refresh_feeds",
        "schedule": crontab(minute=0, hour="*/1"),
    },
}
