"""Telegram notifications for entries, exits, stop-loss hits and summaries.

Fails soft: notification errors never break the trading flow. When the bot is
not configured, messages are logged instead of sent.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.logging_config import get_logger

log = get_logger("notifications.telegram")

_API = "https://api.telegram.org/bot{token}/sendMessage"


def _enabled() -> bool:
    return (
        settings.notifications_enabled
        and bool(settings.telegram_bot_token)
        and bool(settings.telegram_chat_id)
    )


def send(text: str) -> bool:
    if not _enabled():
        log.info("[notify-disabled] %s", text.replace("\n", " ")[:200])
        return False
    try:
        resp = httpx.post(
            _API.format(token=settings.telegram_bot_token),
            json={
                "chat_id": settings.telegram_chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("Telegram send failed: %s", exc)
        return False


def notify_entry(symbol: str, side: str, qty: int, price: float, mode: str) -> None:
    send(
        f"🟢 <b>ENTRY</b> [{mode.upper()}]\n{side} {symbol} x{qty} @ ₹{price:.2f}"
    )


def notify_exit(symbol: str, qty: int, price: float, pnl: float, mode: str) -> None:
    emoji = "✅" if pnl >= 0 else "🔻"
    send(
        f"{emoji} <b>EXIT</b> [{mode.upper()}]\n{symbol} x{qty} @ ₹{price:.2f} "
        f"| PnL ₹{pnl:.2f}"
    )


def notify_stop(symbol: str, price: float, pnl: float) -> None:
    send(f"🛑 <b>STOP LOSS</b>\n{symbol} @ ₹{price:.2f} | PnL ₹{pnl:.2f}")


def notify_daily_summary(text: str) -> None:
    send(f"📊 <b>Daily Summary</b>\n{text}")
