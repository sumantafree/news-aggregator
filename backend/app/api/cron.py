"""Public cron endpoint — called by Render Cron Job (or any scheduler) to refresh feeds.

Protected by a shared secret in the `X-Cron-Secret` header so anyone on the internet
can't trigger ingest. Set CRON_SECRET in your env and configure the scheduler with
the same header value.
"""
from fastapi import APIRouter, Header, HTTPException, BackgroundTasks

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.ingest import ingest_all

router = APIRouter(tags=["cron"])


def _run_ingest():
    db = SessionLocal()
    try:
        ingest_all(db)
    finally:
        db.close()


@router.post("/cron/refresh")
def cron_refresh(
    background: BackgroundTasks,
    x_cron_secret: str | None = Header(default=None, alias="X-Cron-Secret"),
):
    if not settings.CRON_SECRET:
        raise HTTPException(503, "Cron endpoint disabled (CRON_SECRET not configured)")
    if x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(401, "Invalid cron secret")
    background.add_task(_run_ingest)
    return {"ok": True, "message": "Feed refresh scheduled"}
