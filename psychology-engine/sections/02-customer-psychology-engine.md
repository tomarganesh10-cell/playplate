# Section 2 — The Customer Psychology Engine (Customer 360)

> An AI profile for every guest — that makes their next visit better than their last,
> using only what they choose to share, modelling only what they *do and prefer*, never
> who they *are* in a sensitive sense.

---

## 2.1 Design principles for the profile

1. **Consent-tiered.** The profile has capability tiers unlocked by explicit opt-in. With
   zero consent, a guest still gets great generic service. Each additional consent unlocks
   *better* personalisation — never *access*. 🔒
2. **Behaviour over identity.** Every field is a behaviour, a preference, or a
   voluntarily-given fact. There is **no field, anywhere, for a sensitive attribute** —
   and the schema physically forbids one (Section 11).
3. **Explainable & inspectable.** Every derived score is explainable ("your Churn Risk rose
   because it's been 6 weeks since your last visit") and visible to the guest on request.
4. **Decay & recency.** Preferences decay; people change. The profile weights recent
   behaviour but preserves stable long-term identity, and *forgets* on request.
5. **Portable & deletable.** The guest can export or delete the entire profile in one
   action (right to access, right to erasure).

---

## 2.2 The Customer 360 field catalogue

Each field below lists: **type**, **source**, **consent tier**, and a **note**. Consent
tiers: **T0** = operationally necessary (e.g. an order needs an order record); **T1** =
basic personalisation opt-in; **T2** = enhanced personalisation opt-in; **T3** = social/
network features (double opt-in — both parties consent).

### Identity & consent (the root)

| Field | Type | Source | Tier | Note |
|---|---|---|---|---|
| `customer_id` | UUID | System | T0 | Pseudonymous internal key; not a real-world ID. |
| `consent_ledger` | Object | Guest | T0 | Per-purpose consent + timestamp + version. The gatekeeper for everything else. 🔒 |
| `display_name` | String | Guest | T1 | What the avatar/staff greet them as. |
| `birthday` | Date (opt.) | Guest | T1 | Only if volunteered; used for birthday rewards. Month/day sufficient. |
| `relationship_status` | Enum (opt.) | Guest | T2 | **Only if voluntarily provided.** Used only for opt-in relevant offers (e.g. date-night). Never inferred. |
| `contact_prefs` | Object | Guest | T1 | Channels + frequency caps the guest set (Section 10). |

### Psychology & personality (behavioural, derived) 🧠

| Field | Type | How derived | Tier | Note |
|---|---|---|---|---|
| `psychology_score` | 0–100 composite | Weighted blend of engagement, satisfaction, loyalty, healthy-usage signals | T1 | A **health-of-relationship** score, not a judgement of the person. Explainable sub-scores. |
| `personality_type` | Behavioural archetype | Clustering on *behaviour* (see 2.4) | T2 | e.g. "Competitive Squad Player," "Chill Coffee Regular." **Not** a psychometric/clinical type. |
| `decision_style` | Enum | Observed choice behaviour (1.3) | T2 | Maximiser / Satisficer / Habitual / Social. Adapts UI & avatar. |
| `motivation_profile` | Vector | JTBD signals (1.17) | T2 | Situational "why they visit," refreshed per context. |

### Affective state (sentiment, not sensitive inference) — see Section 6 🔒

| Field | Type | How derived | Tier | Note |
|---|---|---|---|---|
| `mood_score` | −1…+1 (session) | *Voluntary* feedback, ratings, service events | T1 | **Session sentiment**, decays fast. Inferred from interactions the guest chose to have — never from covert biometric/facial reading. |
| `emotion_history` | Time series | Rolling `mood_score` + tagged events | T1 | For service recovery & trend, not profiling. Short retention window. |
| `happiness_score` | 0–100 (trend) | Smoothed satisfaction trend | T1 | Relationship-level satisfaction proxy. |
| `stress_score` | 0–100 (context) | *Operational* signals only (long wait, failed order, complaint) | T1 | Flags **service friction to fix**, not a psychological diagnosis. Explicitly **not** a read of the guest's mental health. |

> **Hard rule for this block (Section 11).** These are *satisfaction/sentiment* signals to
> improve service. They are **never** used to infer a health/psychological condition, never
> shared, never used adversely (e.g. to deny service or raise price), and never derived from
> covert biometrics. A low `stress_score` triggers *"go make this right,"* nothing else.

### Behavioural preferences (the useful core)

| Field | Type | Source | Tier |
|---|---|---|---|
| `gaming_behaviour` | Object | Session logs | T1 |
| `food_behaviour` | Object | Order history | T1 |
| `favourite_games` | Ranked list | Sessions | T1 |
| `favourite_food` | Ranked list | Orders | T1 |
| `favourite_drinks` | Ranked list | Orders | T1 |
| `preferred_seating` | Enum/zone | Bookings/behaviour | T2 |
| `preferred_music` | Tags | Voluntary + zone behaviour | T2 |
| `preferred_time` | Distribution | Visit timestamps | T1 |
| `avg_spend` | Currency | Orders | T1 |
| `visit_frequency` | Rate + cadence | Visit history | T1 |

`gaming_behaviour` sub-fields: preferred platforms (PS5/PC/VR/sim), genres, session
length distribution, solo-vs-squad ratio, competitive-vs-casual lean, skill/mastery
trajectory (for flow-matching, 1.21), preferred stations.

`food_behaviour` sub-fields: cuisine/flavour preferences, veg-forward favourites,
sharing-vs-solo, snack-vs-meal, drink pairings, dessert propensity, dietary preferences
*the guest stated* (e.g. "no onion/garlic," "vegan") — stored as **stated preferences**,
never inferred health data.

### Social & community (double opt-in) — T3, 🔒

| Field | Type | Note |
|---|---|---|
| `group_behaviour` | Object | How they behave in a party (organiser? follower?) — from *own* behaviour. |
| `social_behaviour` | Object | Community participation (events, tournaments, creator activity). |
| `friends_network` | Graph edges | **Only with both users' consent.** Used for squad features & (opt-in) social proof. Deletable; either party's opt-out severs the edge. |
| `referral_behaviour` | Object | Referrals made/converted (Section 8). |

### Value & lifecycle (business scores) 🧠 📊

| Field | Type | How derived | Note |
|---|---|---|---|
| `loyalty_score` | 0–100 | Tenure, frequency, tier, engagement | Drives recognition, not gating of basic service. |
| `brand_affinity` | 0–100 | Advocacy, UGC, referrals, sentiment | Identifies champions to nurture. |
| `customer_lifetime_value` | Currency (pred.) | CLV model (Section 12) | With confidence interval; a planning number, not a caste. |
| `churn_risk` | 0–1 (pred.) | Churn model | Triggers *care*, never punishment. |
| `upsell_probability` | 0–1 (pred.) | Propensity model | Ranks *helpful* suggestions; capped by frequency rules. |
| `cross_sell_probability` | 0–1 (pred.) | Propensity model | e.g. gamer likely to enjoy the coffee bar. |
| `impulse_buying_score` | 0–1 | Behavioural | **Guarded field:** used to *tune restraint*, not to exploit. See box below. |

> **The `impulse_buying_score` ethics guard 🔒.** A high impulse score is precisely the
> case where exploitation is tempting and forbidden. PLAYPLATE uses this score to *protect*
> guests: high-impulse + high-frequency-spend patterns trigger **frequency caps and "are you
> sure?" friction**, and (for at-risk or younger guests) spend-limit prompts — the *opposite*
> of pressure. It is **never** used to increase pressure, target vulnerable guests, or raise
> prices. Any use of this field is logged and audited (Section 11).

---

## 2.3 What is deliberately **absent** from the profile 🔒

There is no field, computed or stored, for: health/medical status, disability, mental-
health condition, religion, caste, ethnicity/race, nationality-as-identity, sexual
orientation, gender identity beyond what's volunteered for address/greeting, precise
political views, income/financial status beyond spend-with-us, biometric identity
templates, or precise persistent location tracking. The schema layer **rejects** any
attempt to add such a field (a CI guard tests for it; Section 11 & database-design.md).

`relationship_status` and `birthday` exist **only** because a guest may *volunteer* them
for a benefit they want (date-night offers, birthday rewards) — stored as given, never
inferred, deletable, and never required.

---

## 2.4 How the derived scores are built (methodology) 🧠

Full model specs live in `architecture/ai-models.md`; here is the *what and why*.

- **Personality Type (behavioural archetypes).** Unsupervised clustering (e.g.
  k-means/HDBSCAN) over *behavioural features only* — game genre mix, session style,
  food style, visit cadence, social lean. Output is a human-readable archetype label used
  to tailor tone and suggestions. Archetypes are **descriptions of behaviour patterns**,
  reviewed to ensure they never proxy a protected attribute (fairness audit, Section 11).
- **Decision Style.** A lightweight classifier over choice behaviour (time-to-decide,
  breadth browsed, reorder rate, response to "for you"). Drives *interface* adaptation.
- **Mood / Happiness / Stress (sentiment).** Sentiment models over *voluntary* text/rating
  feedback + rule-based operational signals (wait time, order errors). Short retention,
  fast decay, explainable. Section 6 details the guardrails.
- **CLV, Churn, Upsell, Cross-sell.** Standard supervised propensity/survival models
  (Section 12) with **calibrated probabilities and confidence intervals** — we never show a
  bare point estimate as if it were certain.
- **Composite scores (Psychology/Loyalty/Affinity).** Transparent weighted blends with
  published weights and per-guest explanations. No black-box "worthiness" number.

**Uncertainty is first-class.** Cold-start guests (little data) get *population priors* and
conservative personalisation; the profile clearly marks low-confidence fields so downstream
systems don't over-commit.

---

## 2.5 The consent-tier UX (how a profile grows)

```
 T0  ── First visit / order ─────────▶  Great generic service. Minimal record.
        │  "Want us to remember your favourites?"  → opt-in
 T1  ── Basic personalisation ───────▶  Favourites, "for you," birthday, mood-aware care.
        │  "Want smarter, more tailored suggestions & preferences?" → opt-in
 T2  ── Enhanced personalisation ────▶  Archetype tuning, seating/music/time, decision-style UI.
        │  "Want to connect with friends / squads here?" → double opt-in
 T3  ── Social & community ──────────▶  Friends network, squad features, opt-in social proof.
```

Every arrow is a *clear, plain-language* ask with a preview of the benefit and a one-tap
opt-out. Downgrading a tier immediately deactivates and (on request) deletes the associated
data.

---

## 2.6 Profile lifecycle & governance

- **Creation:** on first opt-in (T1). T0 keeps only what an operation strictly requires.
- **Update:** event-driven (each visit/order/session), with recency-weighted decay.
- **Access:** guest can view the full profile + every derived score's explanation.
- **Correction:** guest can correct any stated fact; behavioural facts are read-only but
  visible.
- **Portability:** one-tap export (machine-readable).
- **Erasure:** one-tap delete → hard-deletes personal data, severs network edges, and
  removes the guest from all models on the next retrain (right to be forgotten). 🔒
- **Retention:** each field has a defined max retention; sentiment/emotion data has the
  *shortest* window (Section 11 retention schedule).

---

## 2.7 How the profile is *used* (and how it is not)

**Used to:** greet warmly, suggest relevant food/games/offers, time a delight, remember a
seat, celebrate a birthday, prevent churn with *care*, recognise loyalty, and route the
right experience to the right guest.

**Never used to:** deny or degrade basic service; charge an individual more; pressure a
vulnerable guest; infer or act on a sensitive attribute; share/sell data; or feed any
decision that materially harms the guest without a human in the loop. (Section 11 is the
enforceable version of this sentence.)

---

### Change log
- v1.0 — Initial Customer 360 specification.
