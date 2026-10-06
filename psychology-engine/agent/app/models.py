"""Pydantic schemas. Note what is deliberately ABSENT: there is no field
anywhere for a sensitive attribute (health, religion, caste, ethnicity,
orientation, biometrics, precise location, wealth). See ../../sections/
11-ethics-privacy.md and ../../architecture/database-design.md."""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field

Purpose = Literal["personalisation", "marketing", "social"]


class ConsentUpdate(BaseModel):
    purpose: Purpose
    granted: bool
    tier: int = Field(0, ge=0, le=3)


class MessageIn(BaseModel):
    customer_id: str
    text: str = Field(..., max_length=500)


class Recommendation(BaseModel):
    id: str
    name: str
    icon: str
    price: int
    kind: Literal["food", "game"]
    why: str            # every recommendation is explained (Section 7)
    score: float


class MessageOut(BaseModel):
    reply: str
    intent: str
    recommendations: list[Recommendation] = []
    # a transparent snapshot of what the Brain currently believes (guest-inspectable)
    profile: dict
    ai_disclosure: str = "You are talking to an AI agent, not a human."


class FeedbackIn(BaseModel):
    customer_id: str
    sentiment: float = Field(..., ge=-1.0, le=1.0)  # from voluntary feedback only


class AcceptIn(BaseModel):
    customer_id: str
    kind: Literal["food", "game"]
    item_id: str
