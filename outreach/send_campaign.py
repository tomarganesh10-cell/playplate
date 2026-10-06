#!/usr/bin/env python3
"""PLAYPLATE partnership outreach mailer.

Sends personalised brand / commercial-leasing emails from partnerships@playplate.in
via Hostinger SMTP, attaches the brand deck, throttles sends, de-duplicates against a
log (so daily runs pick up the next N never-contacted rows), and appends a compliant
footer. DRY-RUN by default — writes .eml files to outbox/ so you can inspect before
anything leaves. Real sending requires --send AND SMTP_PASS in the environment.

Examples
--------
  # 1) Inspect what would go out (no email sent):
  python send_campaign.py --campaign brand --limit 100

  # 2) Actually send today's 100 brand emails (creds from .env / environment):
  python send_campaign.py --campaign brand --send --limit 100

  # 3) Commercial / mall leasing, 50/day:
  python send_campaign.py --campaign commercial --send --limit 50

Config (environment variables; see config.example.env)
  SMTP_HOST   default smtp.hostinger.com
  SMTP_PORT   default 465            (SSL)
  SMTP_USER   default partnerships@playplate.in
  SMTP_PASS   required for --send
  FROM_NAME   default "PLAYPLATE Partnerships"
  VIDEO_URL   link used for {{video_url}} in templates
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "logs" / "sent.csv"
DECK = ROOT / "assets" / "PLAYPLATE_Brand_Deck.pdf"

CAMPAIGNS = {
    "brand":      {"template": "templates/brand.txt",      "recipients": "recipients/brands.csv"},
    "commercial": {"template": "templates/commercial.txt", "recipients": "recipients/commercial.csv"},
}

FOOTER = (
    "\n\n—\n"
    "PLAYPLATE (Eat • Play • Repeat) · Zirakpur, Punjab, India · www.playplate.in\n"
    "This is a one-to-one business partnership enquiry. If you'd prefer not to receive "
    "these emails, reply \"UNSUBSCRIBE\" and we will remove you immediately."
)


# --------------------------------------------------------------------------- #
def load_env_file(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE lines). Real env vars take precedence."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def render(text: str, row: dict) -> str:
    """Replace {{key}} with row[key] (or ''). Adds a couple of derived fields."""
    ctx = dict(row)
    ctx.setdefault("team", "Leasing Team")
    city = (row.get("city") or "").strip()
    ctx["city_suffix"] = f" ({city})" if city else ""
    ctx["video_url"] = row.get("video_url") or os.environ.get("VIDEO_URL", "www.playplate.in")
    out = text
    # replace known keys; leave nothing dangling
    import re
    def sub(m):
        key = m.group(1).strip()
        return str(ctx.get(key, "")).strip()
    return re.sub(r"\{\{\s*([\w_]+)\s*\}\}", sub, out)


def parse_template(path: Path) -> tuple[str, str]:
    raw = path.read_text()
    lines = raw.splitlines()
    subject = ""
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.lower().startswith("subject:"):
            subject = ln.split(":", 1)[1].strip()
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip("\n")
    return subject, body


def load_sent() -> set[str]:
    done: set[str] = set()
    if LOG.exists():
        with LOG.open(newline="") as f:
            for r in csv.DictReader(f):
                if r.get("status") == "sent" and r.get("to_email"):
                    done.add(r["to_email"].strip().lower())
    return done


def log_row(campaign: str, to_email: str, cc: str, subject: str, status: str, error: str = "") -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "campaign", "to_email", "cc", "subject", "status", "error"])
        w.writerow([datetime.now(timezone.utc).isoformat(), campaign, to_email, cc, subject, status, error])


def build_message(from_name: str, from_addr: str, to_addr: str, cc_list: list[str],
                  subject: str, body: str, attach_deck: bool, attach_video: str | None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = to_addr
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    msg["Reply-To"] = from_addr
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain=from_addr.split("@")[-1])
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg.set_content(body + FOOTER)
    if attach_deck and DECK.exists():
        msg.add_attachment(DECK.read_bytes(), maintype="application", subtype="pdf",
                           filename="PLAYPLATE_Brand_Deck.pdf")
    if attach_video:
        vp = Path(attach_video)
        if vp.exists():
            msg.add_attachment(vp.read_bytes(), maintype="video", subtype="mp4", filename=vp.name)
    return msg


def main() -> int:
    ap = argparse.ArgumentParser(description="PLAYPLATE outreach mailer")
    ap.add_argument("--campaign", choices=CAMPAIGNS.keys(), help="brand or commercial")
    ap.add_argument("--template", help="override template path")
    ap.add_argument("--recipients", help="override recipients CSV path")
    ap.add_argument("--limit", type=int, default=100, help="max emails this run (daily cap)")
    ap.add_argument("--send", action="store_true", help="ACTUALLY send (default: dry-run to outbox/)")
    ap.add_argument("--min-delay", type=float, default=30.0, help="min seconds between sends")
    ap.add_argument("--max-delay", type=float, default=60.0, help="max seconds between sends")
    ap.add_argument("--no-deck", action="store_true", help="do not attach the brand deck")
    ap.add_argument("--attach-video", metavar="PATH", help="attach a video file (NOT recommended)")
    args = ap.parse_args()

    load_env_file(ROOT / ".env")

    if args.campaign:
        template_path = ROOT / CAMPAIGNS[args.campaign]["template"]
        recipients_path = ROOT / CAMPAIGNS[args.campaign]["recipients"]
        campaign = args.campaign
    elif args.template and args.recipients:
        template_path = Path(args.template)
        recipients_path = Path(args.recipients)
        campaign = template_path.stem
    else:
        ap.error("provide --campaign, or both --template and --recipients")

    subject_tpl, body_tpl = parse_template(template_path)
    from_addr = os.environ.get("SMTP_USER", "partnerships@playplate.in")
    from_name = os.environ.get("FROM_NAME", "PLAYPLATE Partnerships")
    host = os.environ.get("SMTP_HOST", "smtp.hostinger.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    password = os.environ.get("SMTP_PASS", "")

    if args.send and not password:
        print("ERROR: --send requires SMTP_PASS in the environment (see config.example.env).", file=sys.stderr)
        return 2

    done = load_sent()
    outdir = ROOT / "outbox" / campaign
    outdir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    with recipients_path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    server = None
    if args.send:
        ctx = ssl.create_default_context()
        server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
        server.login(from_addr, password)

    mode = "SEND" if args.send else "DRY-RUN"
    print(f"[{mode}] campaign={campaign} from={from_addr} limit={args.limit} "
          f"already-contacted={len(done)}")

    sent = skipped = failed = 0
    try:
        for row in rows:
            if sent >= args.limit:
                break
            to_addr = (row.get("to_email") or "").strip()
            if not to_addr:
                continue  # no verified email yet -> never guess/blast
            if to_addr.lower() in done:
                skipped += 1
                continue

            cc_raw = (row.get("cc_emails") or "").replace(",", ";")
            cc_list = [c.strip() for c in cc_raw.split(";") if c.strip()]
            subject = render(subject_tpl, row)
            body = render(body_tpl, row)
            msg = build_message(from_name, from_addr, to_addr, cc_list, subject, body,
                                attach_deck=not args.no_deck, attach_video=args.attach_video)

            label = row.get("company") or row.get("venue") or to_addr
            try:
                if args.send:
                    server.send_message(msg)
                else:
                    (outdir / f"{to_addr.replace('@','_at_')}.eml").write_bytes(bytes(msg))
                sent += 1
                done.add(to_addr.lower())
                cc_str = ";".join(cc_list)
                print(f"  ✓ {mode} → {label} <{to_addr}>" + (f"  cc:{len(cc_list)}" if cc_list else ""))
                if args.send:
                    log_row(campaign, to_addr, cc_str, subject, "sent")
                    time.sleep(random.uniform(args.min_delay, args.max_delay))
            except Exception as e:  # noqa: BLE001 - continue on per-recipient failure
                failed += 1
                print(f"  ✗ FAILED → {label} <{to_addr}>: {e}", file=sys.stderr)
                if args.send:
                    log_row(campaign, to_addr, ";".join(cc_list), subject, "failed", str(e))
    finally:
        if server:
            server.quit()

    print(f"\n[{mode}] done: {sent} { 'sent' if args.send else 'previewed'}, "
          f"{skipped} already-contacted, {failed} failed.")
    if not args.send:
        print(f"Inspect drafts in: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
