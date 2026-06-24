"""Background worker.

Runs the periodic scanner during market hours and dispatches daily/weekly
reports to Telegram. This is a deliberately simple loop (no external scheduler
dependency); for higher reliability swap in APScheduler or Celery beat.

The worker NEVER places orders on its own — it only generates signals and
notifications. Order execution always requires an explicit API request.
"""
from __future__ import annotations

import time

from app.broker.session import get_broker
from app.config import settings
from app.database import SessionLocal
from app.engine import market_hours
from app.logging_config import configure_logging, get_logger
from app.notifications import telegram
from app.services.scanner_service import run_scan

configure_logging()
log = get_logger("worker")

SCAN_INTERVAL_SECONDS = 300  # 5 minutes
_last_daily_report_date = None


def _maybe_send_daily_report(db) -> None:
    global _last_daily_report_date
    now = market_hours.now_ist()
    # After market close, once per day.
    if now.time() >= market_hours.MARKET_CLOSE and _last_daily_report_date != now.date():
        from app.ai import reports

        telegram.notify_daily_summary(reports.daily_report(db))
        _last_daily_report_date = now.date()
        log.info("Daily report dispatched for %s", now.date())


def run_once() -> None:
    db = SessionLocal()
    try:
        if market_hours.is_market_open():
            broker = get_broker(db)
            result = run_scan(db, broker)
            log.info("Scan complete: %s qualifying signals", result["count"])
        else:
            log.info("Market closed (%s); skipping scan", market_hours.session_state())
        _maybe_send_daily_report(db)
    except Exception as exc:  # noqa: BLE001
        log.exception("Worker iteration failed: %s", exc)
    finally:
        db.close()


def main() -> None:
    log.info("Worker started (mode=%s)", settings.trading_mode.value)
    while True:
        run_once()
        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
