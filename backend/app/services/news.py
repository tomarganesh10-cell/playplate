"""Market news headlines from public RSS feeds.

Best-effort with a short cache: each feed gets a small timeout, failures are
logged and skipped, and an empty list is a valid (degraded) result. Headlines
are informational only — never used as trading signals.
"""
from __future__ import annotations

import html
import re
import threading
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import httpx

from app.logging_config import get_logger

log = get_logger("services.news")

FEEDS: list[tuple[str, str]] = [
    ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Moneycontrol", "https://www.moneycontrol.com/rss/marketreports.xml"),
    ("Livemint", "https://www.livemint.com/rss/markets"),
]

# Several Indian outlets 403 non-browser user agents on their RSS endpoints.
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

_CACHE_TTL_S = 600.0
_cache: dict = {"ts": 0.0, "items": []}
_lock = threading.Lock()

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    return html.unescape(_TAG_RE.sub("", text)).strip()


def _published_ts(item: dict) -> float:
    try:
        return parsedate_to_datetime(item["published"]).timestamp()
    except Exception:  # noqa: BLE001
        return 0.0


def _fetch_feed(source: str, url: str) -> list[dict]:
    resp = httpx.get(
        url,
        timeout=6.0,
        follow_redirects=True,
        headers={"User-Agent": _UA},
    )
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for it in root.iter("item"):
        title = _clean(it.findtext("title") or "")
        link = (it.findtext("link") or "").strip()
        published = (it.findtext("pubDate") or "").strip()
        if title and link:
            items.append(
                {"source": source, "title": title, "link": link, "published": published}
            )
    return items


def get_market_news(limit: int = 24) -> list[dict]:
    now = time.time()
    with _lock:
        if now - _cache["ts"] < _CACHE_TTL_S and _cache["items"]:
            return _cache["items"][:limit]

    items: list[dict] = []
    for source, url in FEEDS:
        try:
            items.extend(_fetch_feed(source, url))
        except Exception as exc:  # noqa: BLE001
            log.warning("news fetch failed for %s: %s", source, exc)

    items.sort(key=_published_ts, reverse=True)
    if items:
        with _lock:
            _cache["ts"] = now
            _cache["items"] = items
    return items[:limit]
