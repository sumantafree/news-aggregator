from __future__ import annotations

import logging
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.api import admin as admin_api
from app.api import cron as cron_api
from app.api import news as news_api
from app.api import seo as seo_api
from app.api import tracking as tracking_api
from app.bootstrap import run_bootstrap
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.limiter import limiter
from app.services.ingest import ingest_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("news_aggregator")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Dual-Language (Hindi + English) News Aggregator API",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Routers
    app.include_router(news_api.router)
    app.include_router(tracking_api.router)
    app.include_router(admin_api.router)
    app.include_router(cron_api.router)
    app.include_router(seo_api.router)

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "name": settings.APP_NAME,
            "status": "ok",
            "docs": "/docs",
        }

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    @app.on_event("startup")
    def on_startup():
        logger.info("Running bootstrap …")
        run_bootstrap()

        # Kick off an initial ingest in the background so the homepage
        # has data on first load, without blocking startup.
        def _initial_ingest():
            time.sleep(2)
            db = SessionLocal()
            try:
                totals = ingest_all(db)
                logger.info("Initial ingest complete: %s", totals)
            except Exception:
                logger.exception("Initial ingest failed")
            finally:
                db.close()

        threading.Thread(target=_initial_ingest, daemon=True).start()

    return app


app = create_app()
