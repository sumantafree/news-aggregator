from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.click import Click
from app.schemas.news import ClickIn

router = APIRouter(tags=["tracking"])


@router.post("/track")
@limiter.limit("300/minute")
def track_click(
    payload: ClickIn,
    request: Request,
    db: Session = Depends(get_db),
):
    db.add(
        Click(
            article_id=payload.article_id,
            source_name=payload.source_name,
            language=payload.language,
            referer=payload.referer or request.headers.get("referer"),
            user_agent=(request.headers.get("user-agent") or "")[:256],
        )
    )
    db.commit()
    return {"ok": True}
