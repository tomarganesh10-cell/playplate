"""Consent & Ethics Guard (reference).

A slim, in-path version of the guard described in ../../architecture/
system-architecture.md (§3.2). Every personalised read/action is checked
here. It FAILS CLOSED: if consent for a purpose is not granted, the
personalised path does not run and the caller falls back to generic
(still-great) service.

Two other invariants live here:
  * PROHIBITED_FEATURES — a firewall so no sensitive attribute can ever
    enter a decision (Section 11.6).
  * human_gate — Tier C/D actions cannot be auto-executed (Section 10.1).
"""

from __future__ import annotations

# Sensitive-field firewall: these must never appear as inputs to any
# decision. Mirrors the schema/CI guard in the bible (Section 11.2/11.6).
PROHIBITED_FEATURES = frozenset({
    "health", "medical", "disability", "mental_health", "religion", "caste",
    "ethnicity", "race", "nationality", "sexual_orientation", "gender_identity",
    "political", "biometric", "precise_location", "income", "wealth",
})


def assert_no_sensitive_features(features: dict) -> None:
    """Raise if any prohibited feature is present. Call before any model use."""
    bad = PROHIBITED_FEATURES.intersection(features.keys())
    if bad:
        raise ValueError(
            f"Sensitive-field firewall: prohibited features rejected: {sorted(bad)}"
        )


def has_consent(profile: dict, purpose: str) -> bool:
    """Fail-closed consent check."""
    return bool(profile.get("consent", {}).get(purpose, False))


# Risk tiers from Section 10.1. Only A/B may auto-execute.
AUTO_TIERS = frozenset({"A", "B"})


def human_gate(tier: str) -> bool:
    """Return True if the action may auto-execute; False if a human is required."""
    return tier in AUTO_TIERS
