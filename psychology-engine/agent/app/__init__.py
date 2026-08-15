"""PLAYPLATE Psychology Engine — reference agent service.

A minimal, runnable implementation of the "Brain" described in the
PLAYPLATE Psychology AI Bible (../../). It demonstrates the core loop —
understand -> anticipate -> delight — with the bible's guardrails enforced
in code: consent-first, behaviour-not-identity, and human-in-the-loop for
consequential actions.

This is a reference/prototype, not production infrastructure. Storage is
in-memory; wire a real datastore, auth, and the full Consent & Ethics Guard
before production use (see ../../architecture/).
"""

__version__ = "1.0.0"
