# Executive Summary

## The thesis

Hospitality, gaming and food retail are all, at their core, **emotion businesses**. A
customer does not remember the exact price of a burger or the exact frame-rate of a PS5
session; they remember **how the visit made them feel**. The brand that most reliably
manufactures the feeling of *"they get me, I belong here, I want to come back"* wins the
category — and wins it durably, because feeling is far harder for a competitor to copy
than a menu or a price.

PLAYPLATE's strategic bet is to build that feeling **systematically, at scale, with AI** —
across 100 and eventually 1,000+ stores — while treating every guest and every employee
with more respect for their privacy and autonomy than the industry norm, not less.

The Psychology Engine is how we do it.

## What the engine does (in one paragraph)

It maintains a consent-based, continuously-updated understanding of each guest's
**preferences and behaviour** (what they like to eat, play, and when), each employee's
**wellbeing and growth** (self-reported and performance-based), and each store's
**operational rhythm** (demand, staffing, inventory). It turns that understanding into
**small, well-timed, genuinely helpful actions**: the right food suggestion, the right
game reminder, the right reward, the right shift, the right prep order — delivered through
the app, the avatar, the loyalty layer, staff tools and back-office dashboards.

## Why now

1. **The audience is native to it.** Gen Z and Millennials — PLAYPLATE's core — already
   live inside personalised, gamified, avatar-mediated digital experiences. A café that
   behaves like a great game feels normal, even expected, to them.
2. **The data is a natural byproduct of great service** — orders, sessions, bookings,
   loyalty — so we can personalise without ever needing invasive collection.
3. **The models are commoditised.** Recommendation, forecasting, sentiment and
   conversational models are now reliable and affordable enough to run per-store.
4. **Trust is the new moat.** As surveillance-style personalisation triggers backlash and
   regulation, a brand that is *demonstrably* consent-first and privacy-respecting earns a
   loyalty premium competitors cannot buy.

## The seven outcomes we optimise for 📊

| Outcome | Primary metric | Why the engine moves it |
|---|---|---|
| Customer happiness | CSAT / post-visit sentiment | Better-timed, more relevant service |
| Repeat visits | Visit frequency, 30/60/90-day return rate | Habit loops, missions, timely nudges |
| Gaming usage | Sessions/visit, station utilisation | Game recommendations, tournaments, off-peak offers |
| Food sales | Attach rate, avg. basket, food-per-gaming-hour | Contextual food/drink pairing at the right moment |
| Customer Lifetime Value | Predicted CLV, retention curve | Churn prevention + upsell at moments of delight |
| Employee satisfaction | eNPS, retention, self-reported wellbeing | Fair scheduling, growth, recognition, burnout early-warning |
| Brand loyalty & community | Loyalty tier progression, referrals, UGC | Belonging mechanics, creator community, rankings |

## The design philosophy (the "who built it" DNA)

- **McKinsey** — every capability ties to a P&L line and a measurable KPI; nothing is
  built for novelty.
- **DeepMind** — models are rigorous, evaluated, and honest about uncertainty; we ship
  confidence intervals, not false precision.
- **OpenAI** — natural, conversational, avatar-mediated interaction that feels human and
  helpful.
- **Apple** — privacy as a headline feature, radical simplicity in the guest experience,
  taste in every detail.
- **Disney Imagineering** — the store is a stage; the engine is the invisible cast that
  makes every guest feel like the guest of honour.

## Guardrails, stated once, up front 🔒

The engine is deliberately **narrow in what it is allowed to know and do**:

- **Consent-first.** No personalisation without opt-in. Everything works (more genericly)
  without consent; consent unlocks *better*, never *access*.
- **Behaviour, not identity.** We model what people *do and choose*, never who they *are*
  in a sensitive sense. We do not infer health, religion, caste, ethnicity, sexual
  orientation, political views, disability, or precise biometrics — and we technically
  prevent such fields from ever entering a model. (See Section 6 and Section 11.)
- **Human-in-the-loop for people decisions.** For any decision affecting an employee's
  livelihood or a customer's treatment in a materially adverse way, AI may *inform* but a
  human *decides* and is accountable.
- **Right to be forgotten, right to opt out, right to see.** Built into the data model as
  first-class operations, not bolted on.

## The 100 → 1,000 store logic

The engine is designed **multi-tenant and region-federated from day one**: one shared
platform, per-region "Brains," per-store configuration. Each new store inherits the whole
system on opening day, contributes its data to improve region-level models (privacy-
preserving), and reaches "personalisation maturity" within weeks instead of years. The
marginal cost of intelligence per new store trends toward zero; the marginal *value*
compounds as the network of stores, guests and creators grows.

## What success looks like in 24 months

- Every guest who opts in has a living Customer 360 that makes their next visit measurably
  better than their last.
- Every employee has a fair schedule, a visible growth path, and a manager who is alerted
  to their burnout risk *before* they quit — with the employee's own self-report at the
  centre.
- Every store manager opens one dashboard in the morning and knows exactly what today
  needs: staffing, prep, promotions, and which regulars to delight.
- The CEO can see, per region and per store, the causal line from psychology → behaviour →
  revenue — and can prove the engine paid for itself many times over.

Read on. Section 1 grounds everything in the actual science; Sections 2–12 turn that
science into a system; the technical and governance packages turn the system into
something an engineering org can build starting Monday.
