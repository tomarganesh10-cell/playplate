"""Prometheus request-metrics middleware."""
from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.metrics import http_request_latency, http_requests_total


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        # Use the route template (not the raw path) to keep label cardinality low.
        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        http_request_latency.labels(request.method, path).observe(elapsed)
        http_requests_total.labels(request.method, path, str(response.status_code)).inc()
        return response
