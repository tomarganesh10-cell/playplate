"""Lightweight in-process sliding-window rate limiter (per client IP).

For a single-node deployment this is sufficient. For horizontal scaling, back
this with Redis using the same interface.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config import settings


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            dq = self._hits[key]
            cutoff = now - self.window
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= self.max_requests:
                return False
            dq.append(now)
            return True


_limiter = SlidingWindowLimiter(
    settings.rate_limit_requests, settings.rate_limit_window_seconds
)


def rate_limit(request: Request) -> None:
    """FastAPI dependency enforcing the per-IP request budget."""
    client = request.client.host if request.client else "unknown"
    # Honour X-Forwarded-For when behind the nginx proxy.
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        client = fwd.split(",")[0].strip()
    if not _limiter.allow(client):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Slow down.",
        )
