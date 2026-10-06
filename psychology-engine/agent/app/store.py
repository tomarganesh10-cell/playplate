"""In-memory Customer 360 store (reference only).

Swap for a real datastore in production (see ../../architecture/database-
design.md). Every profile here holds only behavioural / consented data and
supports erasure as a first-class operation (right to be forgotten)."""

from __future__ import annotations

import threading
import time
from typing import Optional


def _new_profile(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        # consent ledger — the gatekeeper. Defaults to OFF (opt-in, not opt-out).
        "consent": {"personalisation": False, "marketing": False, "social": False},
        # behavioural / derived (never sensitive)
        "mood": 0.1,               # session sentiment, decays; from voluntary signals only
        "decision_style": "learning",
        "intent": "arriving",
        "fav_food": [],            # ids
        "fav_game": [],            # ids
        "decisions": [],           # rolling behavioural signal for decision-style inference
        "playing": None,
        # loyalty layer
        "coins": 0,
        "xp": 0,
        "level": 1,
        "streak": 1,
        "created_at": time.time(),
    }


class Store:
    def __init__(self) -> None:
        self._data: dict[str, dict] = {}
        self._lock = threading.Lock()

    def get_or_create(self, customer_id: str) -> dict:
        with self._lock:
            p = self._data.get(customer_id)
            if p is None:
                p = _new_profile(customer_id)
                self._data[customer_id] = p
            return p

    def get(self, customer_id: str) -> Optional[dict]:
        return self._data.get(customer_id)

    def erase(self, customer_id: str) -> bool:
        """Right to be forgotten — hard delete (Section 2.6 / 11)."""
        with self._lock:
            return self._data.pop(customer_id, None) is not None


STORE = Store()
