"""Trading circuit breaker.

A process-level latch that halts new order entry when a safety threshold is
breached (daily loss, drawdown, or a manual trip). It must be explicitly reset
by an admin (or at the next trading day) to resume.
"""
from __future__ import annotations

import threading
from datetime import date

from app.logging_config import get_logger
from app.metrics import circuit_breaker_tripped

log = get_logger("risk.circuit_breaker")


class CircuitBreaker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tripped = False
        self._reason: str | None = None
        self._tripped_on: date | None = None
        circuit_breaker_tripped.set(0)

    @property
    def tripped(self) -> bool:
        # Auto-reset on a new trading day.
        if self._tripped and self._tripped_on and self._tripped_on != date.today():
            self.reset("new trading day")
        return self._tripped

    @property
    def reason(self) -> str | None:
        return self._reason

    def trip(self, reason: str) -> None:
        with self._lock:
            if not self._tripped:
                self._tripped = True
                self._reason = reason
                self._tripped_on = date.today()
                circuit_breaker_tripped.set(1)
                log.warning("Circuit breaker TRIPPED: %s", reason)

    def reset(self, note: str = "manual") -> None:
        with self._lock:
            self._tripped = False
            self._reason = None
            self._tripped_on = None
            circuit_breaker_tripped.set(0)
            log.info("Circuit breaker reset (%s)", note)


breaker = CircuitBreaker()
