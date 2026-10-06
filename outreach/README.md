# PLAYPLATE Outreach Mailer

Automated partnership outreach from **partnerships@playplate.in** via Hostinger SMTP:
personalised **brand** emails and **commercial / mall-leasing** emails, with the brand
deck attached, leasing managers CC'd, throttling, de-duplication, and a compliant footer.

> **Nothing sends until you say so.** The script runs in **dry-run** by default (writes
> preview `.eml` files to `outbox/`). Real sending needs `--send` **and** your mailbox
> password in `.env`.

---

## ⚠️ Read this first — protect your domain (this matters more than the code)

You asked for **~150 cold emails/day from a brand-new domain**. If you do that on day one
you will very likely get `playplate.in` **flagged as spam and your Hostinger mailbox
suspended** within days. Do these first or the whole effort backfires:

1. **Set up email authentication for `playplate.in`** — **SPF, DKIM, and DMARC** DNS
   records (Hostinger has one-click guides). Without these, cold email lands in spam.
2. **Warm up the domain.** Don't start at 150/day. Ramp: ~20/day week 1, ~40 week 2, ~70
   week 3, then 100+. New domains that blast get blacklisted.
3. **Use REAL, verified addresses only.** The recipient CSVs ship with target names but
   **blank emails on purpose** — the mailer skips any blank row so it can never blast a
   guessed address. Guessed emails bounce, and bounces destroy your reputation faster than
   anything. Fill in verified emails (find them via LinkedIn, the brand/mall site, or a
   tool like Apollo/Hunter).
4. **Hostinger has sending limits** (shared plans often ~100/hour and a few hundred/day,
   and cold bulk mail can violate their AUP). Keep volume modest; consider a dedicated
   sending service (Zoho ZeptoMail, Amazon SES, Brevo) if you scale up — same script, just
   change `SMTP_HOST`.
5. **Keep the footer.** It's added automatically (physical address + opt-out) — this is
   what keeps you on the right side of anti-spam norms.
6. **Video is linked, not attached.** An 11 MB attachment on every email = spam. Host the
   video and put the link in `VIDEO_URL`.

None of this is me being cautious for its own sake — it's the difference between "100 warm
partnership leads" and "playplate.in can't send email anymore."

---

## Setup

```bash
cd outreach
cp config.example.env .env          # then edit .env with your mailbox password + video link
```

Fill in real emails in:
- `recipients/brands.csv`      — columns: `company, to_email, cc_emails, notes`
- `recipients/commercial.csv`  — columns: `venue, team, city, to_email, cc_emails, notes`

`cc_emails` = one or more leasing-manager addresses separated by `;` (they'll all be CC'd
and receive the mail).

## Preview (safe — sends nothing)

```bash
python3 send_campaign.py --campaign brand --limit 100
python3 send_campaign.py --campaign commercial --limit 50
# open the generated files in outbox/brand/ and outbox/commercial/ to check them
```

## Send for real

```bash
python3 send_campaign.py --campaign brand      --send --limit 100
python3 send_campaign.py --campaign commercial --send --limit 50
```

The script logs every send to `logs/sent.csv` and **skips anyone already contacted**, so
running it daily automatically works through your list — the next 100 brands and next 50
venues each day, never repeating.

## Run it automatically every day (on your Hostinger/VPS)

This repo already deploys to a server (`../deploy/`). Add a cron job **on that server**
(the mailer must run somewhere always-on with your credentials — not in a throwaway
session):

```cron
# sends every weekday at 10:00 (server time). Uses the .env in outreach/.
0 10 * * 1-5  cd /path/to/playplate/outreach && /usr/bin/python3 send_campaign.py --campaign brand      --send --limit 100 >> logs/cron.log 2>&1
5 10 * * 1-5  cd /path/to/playplate/outreach && /usr/bin/python3 send_campaign.py --campaign commercial --send --limit 50  >> logs/cron.log 2>&1
```

(During warm-up, set `--limit` low and raise it weekly.)

## Options

| Flag | Meaning |
|---|---|
| `--campaign brand\|commercial` | pick template + recipient list |
| `--limit N` | max emails this run (your daily cap) |
| `--send` | actually send (default is dry-run to `outbox/`) |
| `--min-delay` / `--max-delay` | seconds between sends (default 30–60; human-paced) |
| `--no-deck` | don't attach the deck |
| `--attach-video PATH` | attach a video (**not recommended** — link it instead) |
| `--template` / `--recipients` | use custom files instead of a named campaign |

## Files

```
outreach/
├── send_campaign.py        the mailer (Python stdlib only — no dependencies)
├── config.example.env      copy to .env and fill in
├── templates/
│   ├── brand.txt           brand partnership email (Subject: on line 1)
│   └── commercial.txt      mall / commercial leasing email
├── recipients/
│   ├── brands.csv          fill in verified brand emails
│   └── commercial.csv      fill in verified venue + leasing-manager emails
├── assets/PLAYPLATE_Brand_Deck.pdf   attached to every email
├── outbox/                 dry-run previews (gitignored)
└── logs/sent.csv           send history + dedup (gitignored)
```

## Editing the copy

Templates are plain text with `{{placeholders}}`. Line 1 must be `Subject: ...`. Available
placeholders: `{{company}}` (brand), `{{venue}}`, `{{team}}`, `{{city}}`, `{{city_suffix}}`,
`{{video_url}}`. Anything you add as a CSV column becomes a usable `{{column}}`.
