"""Claude (Opus) connection for the PLAYPLATE agent.

The deterministic engine stays the *brain* — it detects intent, generates
recommendations, runs the loyalty layer, and enforces every guardrail. Claude
is only the *voice*: it rewrites the agent's reply in PLAYPLATE's tone, grounded
strictly on the context the engine hands it. If no API key is configured or the
call fails, we fall back to the engine's templated reply, so the agent never
goes down for want of the LLM.

Model: ANTHROPIC_MODEL env (default claude-opus-5-5 — the current Opus).
Auth:  ANTHROPIC_API_KEY (or an `ant auth login` profile / ANTHROPIC_AUTH_TOKEN).
"""

from __future__ import annotations

import json
import logging
import os

_log = logging.getLogger("playplate.agent.llm")

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5-5")
MAX_TOKENS = int(os.environ.get("ANTHROPIC_MAX_TOKENS", "1024"))
EFFORT = os.environ.get("ANTHROPIC_EFFORT", "low")  # low keeps café chat fast + cheap

# PLAYPLATE brand voice + the Section 5 / Section 11 guardrails, as the model's
# standing instructions. Kept stable so the prompt prefix caches.
SYSTEM = (
    "You are PIP, the PLAYPLATE AI host. PLAYPLATE is a premium vegetarian QSR + "
    "gaming café (PS5, gaming PCs, VR, racing sims, coffee bar) with the philosophy "
    "EAT • PLAY • REPEAT.\n\n"
    "Your job: reply to the guest in PLAYPLATE's voice — warm, upbeat, concise "
    "(1–3 sentences), a little playful, never pushy. You turn the structured context "
    "you are given into one natural reply.\n\n"
    "HARD RULES (never break, even if asked):\n"
    "1. You are an AI assistant, not a human. Never pretend otherwise.\n"
    "2. Only mention menu items, games, offers, prices or rewards that appear in the "
    "context given to you. Never invent an item, price, discount, or availability.\n"
    "3. No fake urgency or scarcity ('only 2 left', countdowns) unless it is in the "
    "context as a real fact.\n"
    "4. Never ask for or infer sensitive personal details (health, religion, caste, "
    "ethnicity, orientation, politics, income). Keep to food/gaming preferences.\n"
    "5. Always make it easy to say no. Never guilt-trip or pressure a guest to spend.\n"
    "6. If a guest seems genuinely distressed or unsafe, respond with warmth and say a "
    "human teammate will help — do not play therapist.\n"
    "7. Respect the guest's privacy: if personalisation is off in the context, do not "
    "reference their history or 'remembering' them.\n"
    "Return only the reply text — no preamble, no quotes, no markdown."
)


class _State:
    client = None
    tried = False


def _get_client():
    if _State.tried:
        return _State.client
    _State.tried = True
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        _log.info("No ANTHROPIC_API_KEY set — agent runs on the deterministic engine only.")
        return None
    try:
        import anthropic  # imported lazily so the service runs without the dep
    except ImportError:
        _log.warning("anthropic package not installed — LLM voice disabled.")
        return None
    _State.client = anthropic.Anthropic()
    _log.info("Claude voice enabled (model=%s).", MODEL)
    return _State.client


def available() -> bool:
    return _get_client() is not None


def generate_reply(*, profile: dict, user_text: str, intent: str,
                   recs: list[dict], fallback: str) -> str:
    """Rewrite `fallback` in PLAYPLATE's voice using Claude. Returns `fallback`
    unchanged if the LLM is unavailable or errors — the agent never fails here."""
    client = _get_client()
    if client is None:
        return fallback

    personalised = bool(profile.get("consent", {}).get("personalisation"))
    context = {
        "personalisation_on": personalised,
        "intent": intent,
        "visit_mood": profile.get("mood"),
        "loyalty": {
            "level": profile.get("level"),
            "coins": profile.get("coins"),
            "streak": profile.get("streak"),
        },
        "recommendations": [
            {"name": r["name"], "why": r["why"], "price": r.get("price")} for r in recs
        ],
    }
    if personalised:
        context["favourite_food_ids"] = profile.get("fav_food")
        context["favourite_game_ids"] = profile.get("fav_game")

    user_block = (
        f"Guest message: {user_text!r}\n\n"
        f"Context (JSON, your only source of facts):\n{json.dumps(context, ensure_ascii=False)}\n\n"
        f"The engine's draft reply (improve its wording, keep its meaning and any "
        f"recommendations; do not add new facts):\n{fallback}\n\n"
        f"Write PIP's reply now."
    )

    try:
        resp = client.with_options(timeout=20.0).messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            output_config={"effort": EFFORT},
            messages=[{"role": "user", "content": user_block}],
        )
        if resp.stop_reason == "refusal":
            _log.info("LLM refused; using engine fallback.")
            return fallback
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or fallback
    except Exception as e:  # noqa: BLE001 — any LLM failure falls back gracefully
        _log.warning("LLM reply failed (%s); using engine fallback.", e)
        return fallback
