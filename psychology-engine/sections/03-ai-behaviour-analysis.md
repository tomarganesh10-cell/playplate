# Section 3 — AI Behaviour Analysis

> The engine improves service by *observing behaviour it is allowed to observe* and turning
> it into better moments — never by surveilling people. Every signal here is either
> operationally generated (an order, a booking, a session) or consented, and every use is a
> service improvement, not a judgement.

---

## 3.1 The observation charter (read before the signal list) 🔒

1. **Consented or operational only.** We observe transactions and interactions the guest
   knowingly has with us. We do **not** run covert biometric identification, facial-emotion
   inference, persistent individual location tracking, audio eavesdropping, or any
   observation a guest wouldn't expect from "a café that remembers me."
2. **Aggregate by default.** Floor-level signals (footfall, dwell, queue length) are used
   in **aggregate** for operations. Individual-level use requires the guest's tier consent.
3. **Purpose-bound.** Each signal is collected for a stated service purpose and used only
   for that. No repurposing without fresh consent.
4. **Improve, never penalise.** Behaviour observation drives *better service*; it is never
   used to deny service, blacklist (except documented safety/abuse cases via human review),
   or price-discriminate against an individual.
5. **Minimise & decay.** Collect the least that serves the purpose; retain the shortest
   time that serves it (Section 11 retention schedule).

---

## 3.2 The signals — what we observe, how, and why

| Signal | How captured | Individual vs aggregate | Service purpose |
|---|---|---|---|
| **Entry time** | Booking / check-in / POS timestamp | Aggregate (ops); individual (T1) | Staffing & prep forecasting; "welcome back" timing |
| **Walking speed / gait** | ❌ **Not captured** | — | *Deliberately excluded* — see box below |
| **Ordering behaviour** | POS / app order events | Individual (T1) | Reorder ease, "for you," pace of service |
| **Gaming choices** | Station/session logs | Individual (T1) | Game recs, flow-matching, tournament fit |
| **Payment pattern** | POS (tokenised, PCI-scoped) | Individual (T1) | Frictionless checkout, honest split-bill; **never** used to profile wealth |
| **Waiting behaviour** | Queue/order-tracking system | Aggregate primarily | Reduce felt wait (1.25); flag friction |
| **Time spent (dwell)** | Booking/session + zone (aggregate) | Aggregate; individual only if consented | Capacity, comfort, off-peak balancing |
| **Repeat orders** | Order history | Individual (T1) | One-tap "the usual," loyalty |
| **Food preferences** | Order history + stated | Individual (T1) | Recommendations, menu design |
| **Group dynamics** | Party size, booking, split behaviour | Party-level; individual by own behaviour | Whole-party staging, organiser recognition |
| **Reaction to offers** | Offer impression → action events | Individual (T1) | Stop sending irrelevant offers; frequency control |
| **Feedback** | In-app, avatar, staff, surveys | Individual (T1) | Service recovery, sentiment, product |
| **Review history** | Voluntary reviews / linked public reviews (consented) | Individual (T1) | Recovery, reputation, product signals |

> **Why "walking speed" is excluded.** Your brief listed it, and we made a deliberate design
> choice to **not** implement gait/speed tracking. Reading an individual's body-movement to
> infer their state edges into covert biometric surveillance and can proxy sensitive traits
> (age, disability, health). The service value is marginal and the privacy/ethical cost is
> high. We achieve the underlying goal — *is the guest in a hurry or relaxed?* — from
> **consented context** instead (a "quick lunch" order type, time of day, booking length,
> or the guest simply telling us). This is the pattern for the whole section: **when a
> signal is invasive, we find a consented proxy for the underlying need.**

---

## 3.3 From signal to insight to action (the pipeline)

```
 OBSERVE ──▶ AGGREGATE/PROFILE ──▶ INTERPRET ──▶ RECOMMEND ACTION ──▶ (human or automated,
 (event)     (consent gate 🔒)     (model 🧠)     (with guardrails)      per risk tier)
```

- **Low-risk, high-consent, reversible** actions may be automated (e.g. surfacing "your
  usual" or a relevant game). See Section 10 automation tiers.
- **Anything affecting price, access, or a person adversely** requires a human decision.

**Example — turning observation into a better moment (the good version):**
> A T1 guest books a 2-hour PS5 session at 7pm on a Friday, as they often do with their
> squad. The engine (a) pre-warms their preferred station and saved settings, (b) suggests
> a shareable, one-handed "gaming-friendly" platter their squad has enjoyed, (c) times a
> mid-session "want a cold brew round?" prompt, and (d) at the end, celebrates a squad win
> with bonus coins and a warm send-off. Every step used consented, operational behaviour to
> make the visit better. Nothing inferred a sensitive trait; nothing pressured them.

---

## 3.4 Group & family dynamics (behavioural, consent-safe)

The engine recognises *party patterns from behaviour*: who booked, party size, whether
this looks like a family/kids party (from booking type and order mix, not from profiling
individuals), and who the **organiser** is (the repeat booker/payer — a high-value persona
to delight). It stages the whole party (1.20) and *never* builds unconsented profiles of
other party members, especially children (Section 11).

---

## 3.5 Reaction-to-offers & the "stop bothering me" principle

Every offer is an experiment with an outcome. If a guest ignores or dismisses a category of
offer, the engine **learns to stop**, fast. Frequency caps, easy mute, and "why am I seeing
this?" transparency are built in. The objective function explicitly penalises *annoyance*
(dismissals, opt-outs) — sending fewer, better-timed, more relevant prompts is a design
goal, not a compromise (Section 7, Section 10).

---

## 3.6 Feedback & review handling

- **Multi-channel capture** — app, avatar (Section 5), staff, QR, and (consented) public
  reviews.
- **Real-time recovery** — a negative signal triggers a *service-recovery* workflow
  (reciprocity-driven over-correction, 1.9) with a human where warranted.
- **Closed loop** — the guest sees that their feedback changed something ("you said the
  wait was long — here's what we did").
- **Product signal** — aggregated feedback feeds menu, game, and ops decisions
  (dashboards, Section 9).

---

## 3.7 What behaviour analysis must never become 🔒

A short, enforceable list, repeated because it matters:

- No covert biometric or facial-emotion surveillance.
- No gait/movement or persistent individual location tracking.
- No audio eavesdropping.
- No wealth/health/identity inference from payment or behaviour.
- No adverse individual decisions (price, access, service quality) driven automatically by
  behaviour scores.
- No secret watchlists; any safety/abuse action is human-reviewed, documented, appealable.

The technical enforcement of this list is in Section 11 and `architecture/system-
architecture.md` (the Consent & Ethics Guard sits in the request path for every read/write).

---

### Change log
- v1.0 — Initial behaviour-analysis specification.
