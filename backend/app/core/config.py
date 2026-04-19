from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NewsAggregator"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+psycopg2://news:news@localhost:5432/newsdb"
    REDIS_URL: str | None = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    RSS_REFRESH_INTERVAL: int = 600
    CACHE_TTL_SECONDS: int = 600

    SITE_URL: str = "http://localhost:3000"

    # Shared secret used by the public /cron/refresh endpoint (Render Cron / UptimeRobot / etc).
    # Leave empty to disable the endpoint.
    CRON_SECRET: str = ""

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
