"""Redis cache with in-memory fallback."""
from __future__ import annotations

import json
import time
from typing import Any, Optional

from app.core.config import settings

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class _MemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            return None
        expires, value = item
        if expires and expires < time.time():
            self._store.pop(key, None)
            return None
        return value

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = (time.time() + ttl, value)

    def delete(self, *keys: str) -> None:
        for k in keys:
            self._store.pop(k, None)

    def keys(self, pattern: str) -> list[str]:
        # Simple glob: only support prefix*
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in self._store.keys() if k.startswith(prefix)]
        return [k for k in self._store.keys() if k == pattern]


class Cache:
    def __init__(self) -> None:
        self._client: Any = None
        self._memory = _MemoryCache()
        if redis and settings.REDIS_URL:
            try:
                self._client = redis.Redis.from_url(
                    settings.REDIS_URL, decode_responses=True, socket_timeout=2
                )
                self._client.ping()
            except Exception:
                self._client = None

    def get_json(self, key: str) -> Any:
        raw = self._get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        ttl = ttl or settings.CACHE_TTL_SECONDS
        self._set(key, json.dumps(value, default=str), ttl)

    def delete_prefix(self, prefix: str) -> None:
        if self._client is not None:
            try:
                for k in self._client.scan_iter(f"{prefix}*"):
                    self._client.delete(k)
                return
            except Exception:
                pass
        for k in self._memory.keys(f"{prefix}*"):
            self._memory.delete(k)

    # internal
    def _get(self, key: str) -> Optional[str]:
        if self._client is not None:
            try:
                return self._client.get(key)
            except Exception:
                pass
        return self._memory.get(key)

    def _set(self, key: str, value: str, ttl: int) -> None:
        if self._client is not None:
            try:
                self._client.setex(key, ttl, value)
                return
            except Exception:
                pass
        self._memory.setex(key, ttl, value)


cache = Cache()
