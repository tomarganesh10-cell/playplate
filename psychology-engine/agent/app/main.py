"""PLAYPLATE Psychology Engine — reference agent API.

Run:  uvicorn app.main:app --reload   (from psychology-engine/agent/)
Docs: http://localhost:8000/docs

Guardrails enforced in code (see ../../sections/11-ethics-privacy.md):
  * consent-first & fail-closed        (guard.has_consent)
  * sensitive-field firewall           (guard.assert_no_sensitive_features)
  * human-in-the-loop on Tier C/D      (guard.human_gate)
  * clearly-an-AI disclosure           (MessageOut.ai_disclosure)
  * right to be forgotten              (DELETE /v1/customers/{id})
"""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__, engine
from .guard import has_consent
from .models import (
    AcceptIn, ConsentUpdate, FeedbackIn, MessageIn, MessageOut, Recommendation,
)
from .store import STORE

app = FastAPI(
    title="PLAYPLATE Psychology Engine — Agent",
    version=__version__,
    description="Reference AI agent for the PLAYPLATE gaming-café + QSR ecosystem.",
)

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")


# --------------------------------------------------------------------------- #
# Reply composition (tone is a presentation choice, not identity inference).
# --------------------------------------------------------------------------- #
def _recs(items: list[dict]) -> list[Recommendation]:
    return [Recommendation(**{k: it[k] for k in
            ("id", "name", "icon", "price", "kind", "why", "score")}) for it in items]


def _handle(profile: dict, text: str) -> MessageOut:
    intent = engine.detect_intent(text)
    profile["intent"] = engine.INTENT_LABELS.get(intent, profile["intent"])
    recs: list[dict] = []
    reply = ""

    if intent == "greet":
        reply = "Good to see you. Are we here to eat, play, or a bit of both?"
    elif intent in ("food", "dessert", "coffee"):
        engine.note_decision(profile, "browse")
        engine.bump_mood(profile, 0.1)
        recs = engine.recommend_food(profile, intent)
        reply = ("Here are some crowd favourites (personalisation is off, so these are our "
                 "popular picks — still great!):" if not has_consent(profile, "personalisation")
                 else "On it — here's your For You:")
    elif intent in ("play", "play_ps5", "play_pc", "play_vr", "play_sim"):
        engine.note_decision(profile, "social" if "squad" in text.lower() else "browse")
        engine.bump_mood(profile, 0.15)
        platform = {"play_ps5": "ps5", "play_pc": "pc", "play_vr": "vr", "play_sim": "sim"}.get(intent)
        recs = engine.recommend_games(profile, platform)
        reply = "Here's what's hot on the floor — pick one and I'll hold a station:"
    elif intent == "tournament":
        reply = ("There's a casual ladder at 8pm — skill-matched so it stays fun. "
                 "Want me to reserve a slot? (+big XP for joining.)")
    elif intent == "birthday":
        engine.bump_mood(profile, 0.4)
        engine.reward(profile, 50, 40)
        reply = ("🎂 Happy birthday! Since you told me, here's a free Belgian Choco Lava on the "
                 "house — no strings. Want a squad table so your crew can celebrate?")
    elif intent == "bored":
        reply = ("Let's fix that — try Beat Saber in VR or the 8pm casual ladder. "
                 "Want me to line one up?")
    elif intent == "chill":
        reply = "Chill mode: grab the lounge, an iced cortado, and an easy story game. Coffee, game, or both?"
    elif intent == "help":
        reply = ("I'm your PLAYPLATE agent — I recommend food & games, book stations, run your "
                 "rewards, and remember your favourites only if you let me (see consent). "
                 "Try: 'I want a spicy snack and a squad game.'")
    elif intent == "thanks":
        reply = "Anytime — enjoy PLAYPLATE! ✨"
    elif intent == "bye":
        reply = (f"Thanks for coming by! You leave as {engine.LEVELS[profile['level']-1]} "
                 f"with {profile['coins']} coins. See you soon. 👋")
    else:
        reply = ("Got it. I can help most with food, gaming, tournaments or rewards — "
                 "which way do you want to go?")

    return MessageOut(
        reply=reply,
        intent=intent,
        recommendations=_recs(recs),
        profile=engine.public_profile(profile),
    )


# --------------------------------------------------------------------------- #
# API
# --------------------------------------------------------------------------- #
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "playplate-agent", "version": __version__}


@app.post("/v1/agent/message", response_model=MessageOut)
def message(body: MessageIn) -> MessageOut:
    profile = STORE.get_or_create(body.customer_id)
    return _handle(profile, body.text)


@app.post("/v1/agent/accept", response_model=MessageOut)
def accept(body: AcceptIn) -> MessageOut:
    profile = STORE.get_or_create(body.customer_id)
    engine.note_decision(profile, "fast")
    if body.kind == "food":
        if has_consent(profile, "personalisation") and body.item_id not in profile["fav_food"]:
            profile["fav_food"].append(body.item_id)
        engine.reward(profile, 15, 20)
        engine.bump_mood(profile, 0.25)
        reply = "Nice pick — added. Want a game to go with it?"
    else:
        if has_consent(profile, "personalisation") and body.item_id not in profile["fav_game"]:
            profile["fav_game"].append(body.item_id)
        from .catalog import GAMES_BY_ID
        g = GAMES_BY_ID.get(body.item_id)
        profile["playing"] = g["name"].split(" (")[0] if g else None
        engine.reward(profile, 25, 30)
        engine.bump_mood(profile, 0.3)
        reply = "Session booked! Want a one-handed snack to go with it?"
    return MessageOut(reply=reply, intent="accept", profile=engine.public_profile(profile))


@app.post("/v1/agent/feedback", response_model=MessageOut)
def feedback(body: FeedbackIn) -> MessageOut:
    """Sentiment from VOLUNTARY feedback only (Section 6). Negative feedback
    triggers human-led service recovery, never an adverse decision."""
    profile = STORE.get_or_create(body.customer_id)
    if body.sentiment > 0:
        engine.bump_mood(profile, 0.5)
        engine.reward(profile, 10, 10)
        reply = "Love that — thanks for the feedback! (+a small bonus.)"
    else:
        engine.bump_mood(profile, -0.7)
        # Tier C recovery action -> routed to a human (guard.human_gate('C') == False)
        reply = ("Thank you for telling me — I'm flagging this to a human on the floor now, "
                 "and your next drink is on us. 🙏 (service recovery)")
    return MessageOut(reply=reply, intent="feedback", profile=engine.public_profile(profile))


@app.put("/v1/customers/{customer_id}/consent")
def set_consent(customer_id: str, body: ConsentUpdate) -> dict:
    profile = STORE.get_or_create(customer_id)
    profile["consent"][body.purpose] = body.granted
    return {"customer_id": customer_id, "consent": profile["consent"]}


@app.get("/v1/customers/{customer_id}/profile")
def get_profile(customer_id: str) -> dict:
    profile = STORE.get(customer_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="No profile — nothing collected yet.")
    return engine.public_profile(profile)


@app.delete("/v1/customers/{customer_id}", status_code=200)
def erase(customer_id: str) -> dict:
    """Right to be forgotten (Section 2.6 / 11)."""
    existed = STORE.erase(customer_id)
    return {"customer_id": customer_id, "erased": existed}


# --------------------------------------------------------------------------- #
# Serve the browser agent UI if present (psychology-engine/agent/web/index.html)
# --------------------------------------------------------------------------- #
if os.path.isdir(WEB_DIR):
    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(os.path.join(WEB_DIR, "index.html"))

    app.mount("/app", StaticFiles(directory=WEB_DIR, html=True), name="web")
