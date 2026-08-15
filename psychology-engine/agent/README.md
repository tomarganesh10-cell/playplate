# PLAYPLATE Agent — runnable reference service

A minimal, **deployable** implementation of the "Brain" from the
[PLAYPLATE Psychology AI Bible](../README.md). It's the design bible turned
into working code you can run, containerise, and deploy — with the bible's
guardrails enforced in the code itself.

> **Scope:** a reference/prototype (in-memory storage, keyword intent, no
> external LLM). It demonstrates the architecture and guardrails end-to-end.
> Before production, swap in a real datastore + auth + the full Consent &
> Ethics Guard and intent/recommender models (see [`../architecture/`](../architecture/)).

---

## What it does

- **Conversational agent** (`/v1/agent/message`) — detects intent, adapts, and
  returns recommendations **with a plain-language "why"** (Section 7).
- **Live Customer 360** — mood (from voluntary signals), decision style,
  favourites, loyalty (level/coins/XP/streak) — all **behavioural, never
  sensitive** (Section 2).
- **Loyalty layer** (`/v1/agent/accept`) — earn coins/XP, level up (Section 8).
- **Emotion / service recovery** (`/v1/agent/feedback`) — negative feedback
  routes to a **human** (Section 6).
- **Consent + data rights** — opt-in gating and one-call erasure (Section 11).
- **Browser UI** — the full agent front-end is served at `/` (same experience
  as the hosted demo).

## Guardrails enforced in code

| Guardrail | Where | Bible |
|---|---|---|
| Consent-first, fail-closed | `guard.has_consent` (personalisation defaults **off**) | §11.4 |
| Sensitive-field firewall | `guard.assert_no_sensitive_features` (raises on any prohibited feature) | §11.6 |
| Human-in-the-loop (Tier C/D) | `guard.human_gate` (recovery/comp not auto-executed) | §10.1 |
| Clearly an AI | `MessageOut.ai_disclosure` on every reply | §5.8 |
| Right to be forgotten | `DELETE /v1/customers/{id}` | §2.6 |
| Personalisation never gates basic service | consent-off path returns popular picks, not errors | §2.1 |

---

## Run it

### Local (Python 3.12+)
```bash
cd psychology-engine/agent
pip install -r requirements.txt
uvicorn app.main:app --reload
# UI:   http://localhost:8000/
# Docs: http://localhost:8000/docs
```

### Docker
```bash
cd psychology-engine/agent
docker build -t playplate-agent .
docker run -p 8000:8000 playplate-agent
```

---

## Try the API

```bash
# 1) Talk to the agent (no consent yet -> generic, still-great service)
curl -s localhost:8000/v1/agent/message \
  -H 'content-type: application/json' \
  -d '{"customer_id":"guest-1","text":"I want a spicy snack and a squad game"}'

# 2) Opt in to personalisation
curl -s -X PUT localhost:8000/v1/customers/guest-1/consent \
  -H 'content-type: application/json' \
  -d '{"purpose":"personalisation","granted":true,"tier":2}'

# 3) Accept a game -> earn rewards, learn a favourite
curl -s localhost:8000/v1/agent/accept \
  -H 'content-type: application/json' \
  -d '{"customer_id":"guest-1","kind":"game","item_id":"valorant"}'

# 4) Give voluntary feedback (negative -> human service recovery)
curl -s localhost:8000/v1/agent/feedback \
  -H 'content-type: application/json' \
  -d '{"customer_id":"guest-1","sentiment":-0.8}'

# 5) See the transparent, guest-inspectable profile
curl -s localhost:8000/v1/customers/guest-1/profile

# 6) Right to be forgotten
curl -s -X DELETE localhost:8000/v1/customers/guest-1
```

---

## Layout

```
agent/
├── app/
│   ├── main.py       FastAPI app + endpoints + reply composition
│   ├── engine.py     intent, decision-style, recommender, loyalty
│   ├── guard.py      Consent & Ethics Guard (firewall, consent, human-gate)
│   ├── catalog.py    menu + games (behavioural tags only)
│   ├── models.py     pydantic schemas (no sensitive fields — by design)
│   └── store.py      in-memory Customer 360 (swap for a real datastore)
├── web/index.html    browser agent UI (served at /)
├── Dockerfile
└── requirements.txt
```

## Where to take it next

Follow the [implementation roadmap](../delivery/implementation-roadmap.md):
add persistence + auth, replace keyword intent with the model stack
([`../architecture/ai-models.md`](../architecture/ai-models.md)), stand up the
event backbone and dashboards, and put the production Consent & Ethics Guard
in the request path ([`../architecture/system-architecture.md`](../architecture/system-architecture.md)).
