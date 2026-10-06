"""The agent brain: intent detection, decision-style inference, a guest-value
recommender, the loyalty layer, and reply generation.

Mirrors Sections 2, 3, 6, 7 and 8 of the bible. All personalisation is gated
by the Consent & Ethics Guard; with consent OFF the guest still gets great,
generic service (popular picks) — never a degraded one."""

from __future__ import annotations

import random
from datetime import datetime

from .catalog import FOOD, GAMES, FOOD_BY_ID, GAMES_BY_ID
from .guard import has_consent, assert_no_sensitive_features

LEVELS = ["Rookie", "Player", "Pro", "Legend", "Creator"]
XP_STEP = 100


# --------------------------------------------------------------------------- #
# Intent detection (keyword-based reference; a real deployment would use an
# intent model — see ../../architecture/ai-models.md §12).
# --------------------------------------------------------------------------- #
def detect_intent(text: str) -> str:
    t = f" {text.lower()} "

    def has(*words: str) -> bool:
        return any(w in t for w in words)

    if has(" bye ", "leaving", "heading out"):
        return "bye"
    if has("birthday", "b'day", "bday"):
        return "birthday"
    if has("tournament", "compete", "esports", "ranked"):
        return "tournament"
    if has("bored", "boring", "nothing to do"):
        return "bored"
    if has("help", "how do", "what can you", "confused"):
        return "help"
    if has("dessert", "sweet", "lava", "cake", "choco"):
        return "dessert"
    if has("coffee", "cold brew", "cortado", "filter", "latte"):
        return "coffee"
    if has("hungry", "eat", "food", "snack", "order", "paneer", "nachos", "fries", "wrap", "slider"):
        return "food"
    if has("ps5", "playstation", "fc25", "fifa", "tekken", "god of war"):
        return "play_ps5"
    if has("valorant", "cs2", "counter", " pc "):
        return "play_pc"
    if has(" vr ", "beat saber", "virtual"):
        return "play_vr"
    if has("sim", "racing", "f1", "race"):
        return "play_sim"
    if has("play", "game", "gaming", "squad", "friends"):
        return "play"
    if has("chill", "relax", "vibe", "hang"):
        return "chill"
    if has("thanks", "thank you", "great", "awesome", "love"):
        return "thanks"
    if has("hi", "hey", "hello", "yo", "sup", "namaste"):
        return "greet"
    return "unknown"


INTENT_LABELS = {
    "food": "ordering", "dessert": "celebrating", "coffee": "winding down",
    "play": "here to play", "play_ps5": "PS5 session", "play_pc": "PC session",
    "play_vr": "VR session", "play_sim": "racing", "chill": "relaxing",
    "birthday": "celebrating 🎂", "tournament": "competing", "bored": "needs a spark",
}


# --------------------------------------------------------------------------- #
# Decision-style inference (Section 1.3 / 2.4) — behavioural only.
# --------------------------------------------------------------------------- #
_STYLE_MAP = {
    "fast": "Satisficer — wants a great pick fast",
    "browse": "Maximiser — likes options",
    "social": "Social — follows the squad",
    "habit": "Habitual — loves the usual",
}


def note_decision(profile: dict, kind: str) -> None:
    d = profile["decisions"]
    d.append(kind)
    profile["decisions"] = d[-6:]
    counts: dict[str, int] = {}
    for k in profile["decisions"]:
        counts[k] = counts.get(k, 0) + 1
    top = max(counts, key=counts.get)
    profile["decision_style"] = _STYLE_MAP[top] if len(profile["decisions"]) >= 2 else "learning"


# --------------------------------------------------------------------------- #
# Recommender (Section 7). Guest-value objective: relevance + context, with a
# consent gate. Every item carries a plain-language "why".
# --------------------------------------------------------------------------- #
def _time_ctx() -> str:
    h = datetime.now().hour
    if 5 <= h < 11:
        return "morning"
    if 11 <= h < 16:
        return "afternoon"
    if 16 <= h < 22:
        return "evening"
    return "late"


def recommend_food(profile: dict, intent: str) -> list[dict]:
    # Firewall: prove the feature set is clean before scoring (Section 11.6).
    assert_no_sensitive_features({"intent": intent, "time": _time_ctx()})
    personalised = has_consent(profile, "personalisation")
    ctx = _time_ctx()
    out = []
    for it in FOOD:
        score = random.random() * 0.4
        why = []
        if intent == "dessert" and "dessert" in it["tags"]:
            score += 3; why.append("a sweet finish")
        if intent == "coffee" and "coffee" in it["tags"]:
            score += 3; why.append("your coffee mood")
        if profile["playing"] and it["gaming_friendly"]:
            score += 1.4; why.append(f"one-handed for your {profile['playing']} session")
        if personalised and it["id"] in profile["fav_food"]:
            score += 2.2; why.append("you loved it before")
        if ctx == "morning" and "morning" in it["tags"]:
            score += 1.0; why.append("perfect for mornings")
        if ctx == "evening" and "share" in it["tags"]:
            score += 0.8; why.append("great to share tonight")
        if "hero" in it["tags"]:
            score += 0.9
        if not why:
            why.append("popular tonight" if "share" in it["tags"] else "a house favourite")
        out.append({**it, "kind": "food", "why": why[0], "score": round(score, 3)})
    out.sort(key=lambda r: r["score"], reverse=True)
    n = 2 if intent in ("dessert", "coffee") else 3
    return out[:n]


def recommend_games(profile: dict, platform: str | None) -> list[dict]:
    assert_no_sensitive_features({"platform": platform or "any"})
    personalised = has_consent(profile, "personalisation")
    pool = [g for g in GAMES if (platform is None or g["platform"] == platform)] or GAMES
    out = []
    for g in pool:
        score = random.random() * 0.4
        why = []
        if personalised and g["id"] in profile["fav_game"]:
            score += 2.2; why.append("you've played it here before")
        if "squad" in g["tags"]:
            score += 0.9; why.append("perfect with your squad")
        if "competitive" in g["tags"]:
            score += 0.6; why.append("skill-matched, casual ladder tonight")
        if not why:
            why.append("trending on the floor right now")
        out.append({**g, "kind": "game", "why": why[0], "score": round(score, 3)})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:3]


# --------------------------------------------------------------------------- #
# Loyalty layer (Section 8). Rewards for genuine engagement; no gambling.
# --------------------------------------------------------------------------- #
def reward(profile: dict, coins: int, xp: int) -> list[str]:
    notes = []
    profile["coins"] += coins
    profile["xp"] += xp
    while profile["xp"] >= XP_STEP and profile["level"] < len(LEVELS):
        profile["xp"] -= XP_STEP
        profile["level"] += 1
        notes.append(f"★ LEVEL UP — you're now {LEVELS[profile['level'] - 1]}!")
    notes.append(f"+{coins} coins · +{xp} XP")
    return notes


def bump_mood(profile: dict, delta: float) -> None:
    profile["mood"] = max(-1.0, min(1.0, profile["mood"] + delta))


def public_profile(profile: dict) -> dict:
    """A transparent, guest-inspectable snapshot (Section 9.5). Respects the
    consent gate — with personalisation off, learned data is hidden."""
    personalised = has_consent(profile, "personalisation")
    m = profile["mood"]
    mood_label = ("delighted" if m > 0.5 else "happy" if m > 0.05 else
                  "neutral" if m > -0.25 else "unsettled" if m > -0.6 else "upset")
    return {
        "mood": round(m, 2),
        "mood_label": mood_label,
        "decision_style": profile["decision_style"] if personalised else "paused",
        "intent": profile["intent"],
        "favourites": (
            {"food": [FOOD_BY_ID[i]["name"] for i in profile["fav_food"] if i in FOOD_BY_ID],
             "games": [GAMES_BY_ID[i]["name"] for i in profile["fav_game"] if i in GAMES_BY_ID]}
            if personalised else "paused"
        ),
        "loyalty": {
            "level": profile["level"], "level_name": LEVELS[profile["level"] - 1],
            "coins": profile["coins"], "xp": profile["xp"], "xp_to_next": XP_STEP,
            "streak": profile["streak"],
        },
        "consent": profile["consent"],
    }
