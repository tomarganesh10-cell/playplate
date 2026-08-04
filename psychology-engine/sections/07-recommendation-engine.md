# Section 7 — AI Recommendation Engine

> The right suggestion, to the right guest, at the right moment, for a reason they'd agree
> with — recommending based on **behaviour and context**, never on sensitive personal
> traits, and always easy to decline.

---

## 7.1 Objective — what "good" means

The ranking objective is **not** "maximise this order." It is a blend, explicitly weighting
guest value:

```
 score(item | guest, context) =
        w1 · relevance(guest behaviour, context)      ← dominant term
      + w2 · predicted guest satisfaction / delight
      + w3 · business value (margin, strategic push)  ← bounded, never dominant
      − w4 · annoyance risk (frequency, past dismissals)
      − w5 · guardrail penalties (unhealthy pressure, repetition, over-spend risk)
```

- **Relevance and satisfaction dominate.** A recommendation the guest loves builds the
  lifetime value that a single pushy upsell can't. (McKinsey DNA: optimise CLV, not the next
  transaction.)
- **Annoyance is penalised.** Sending fewer, better suggestions is the goal.
- **Guardrails subtract.** Anything that pressures, exploits impulse (2.2 guard), or
  over-repeats is down-weighted or blocked.

Weights are per-surface, A/B-tested, and audited for fairness (Section 11).

---

## 7.2 What we recommend (per your brief) — and the *moment* that makes it land

| Recommendation | Best moment (context) | Signal basis |
|---|---|---|
| **Food** | On booking a session; mid-session lull; arrival hungry | Order history, context, time, party |
| **Games** | Browsing, post-arrival, between sessions | Session history, genre mix, flow-match (1.21) |
| **Offers** | Off-peak fill; win-back; reward moments | Behaviour, churn risk, off-peak demand (Section 12) |
| **Membership** | After 2–3 great visits (value proven) | Visit frequency, spend, engagement |
| **Birthday rewards** | Birthday window (if volunteered) | `birthday` (opt-in only) |
| **Events** | When they match a guest's interests | Game/genre/community interests |
| **Tournament invitations** | Skill- and interest-matched | Competitive lean, skill trajectory |
| **Coffee** | Wind-down, mornings, pairings | Drink history, time of day, zone |
| **Desserts** | Celebrations, meal-end, relaxed dwell | Dessert propensity, occasion |
| **Merchandise** | High-pride moments (post-win, tier-up) | Affinity, achievement (1.28) |

**Context is the multiplier.** The same guest gets a *shareable platter* suggestion for a
Friday squad night and a *cortado + dessert* for a solo Sunday wind-down. Context = time,
day, party size, zone, current activity, recent behaviour, and (consented) occasion.

---

## 7.3 How it works (models) 🧠 🧩

A layered recommender (`architecture/ai-models.md` has full specs):

1. **Candidate generation**
   - *Collaborative filtering* — "guests like you (behaviourally) enjoyed…"
   - *Content-based* — item features matched to the guest's demonstrated preferences.
   - *Contextual bandits* — learn what works in each context, balancing explore/exploit.
   - *Sequence models* — "what tends to come next" in a visit (session → snack → dessert).
2. **Ranking** — the objective in 7.1, with business + guardrail terms.
3. **Filtering (the guard) 🔒** — remove: things they dislike/are allergic-to (*stated*
   preferences), over-frequent repeats, guardrail-flagged items, and anything relying on a
   sensitive attribute (which can't happen — those features aren't in the model).
4. **Explanation** — every recommendation ships a plain reason ("because you loved X",
   "popular with your squad tonight", "new this week") and an easy dismiss + "show fewer
   like this."

---

## 7.4 Cold start & discovery

- **New guest (T0/T1):** popular, well-loved, and beginner-friendly items + broad discovery
  (population priors). Conservative; no over-personalising on thin data (2.4).
- **Exploration:** the bandit deliberately introduces *some* novelty so guests discover new
  favourites and don't get trapped in a filter bubble (a known personalisation risk we
  design against — diversity is a ranking term).
- **Serendipity slots:** a reserved "try something new?" slot keeps the experience fresh
  (novelty-within-safety, 1.15).

---

## 7.5 Cross-sell & upsell — the *helpful* way

- **Cross-sell** — introduce a gamer to the coffee bar, a coffee regular to a chill VR
  experience, a solo player to a squad night. Bridge worlds the guest would enjoy.
- **Upsell** — offer the *better-fit* option (a combo that genuinely saves money, the sim
  they'd love more than the game they picked), not just the pricier one.
- **Frequency-capped & annoyance-aware** — never the same push twice in a visit; back off
  fast on dismissal (Section 3.5).
- **Impulse guard 🔒** — high-impulse or younger guests get *fewer* prompts and gentle
  spend awareness, not more pressure (2.2).

---

## 7.6 Channels & timing

Recommendations surface through the **app "For You,"** the **avatar** (Section 5), **in-venue
screens/kiosks** (context-appropriate, non-creepy — floor-level, not "we're watching you"),
and **opt-in messaging** (Section 10) — always within the guest's frequency caps and channel
preferences. The engine picks the *least intrusive effective channel* and the *right
moment*, and stays silent when nothing is genuinely worth saying.

---

## 7.7 Measuring success 📊

Primary metrics are guest-centric: **recommendation acceptance *satisfaction*** (did they
like it *after*?), **repeat-visit lift**, **discovery rate** (new favourites found),
**annoyance rate** (dismissals/opt-outs — minimise), and only then **attach/basket lift**
and **CLV lift**. A recommender that raised short-term spend but annoyed guests or hurt
retention is a *failure* by our scorecard (delivery/kpis.md).

---

## 7.8 Guardrails, restated 🔒

- Recommend on **behaviour & context**, never sensitive traits (structurally impossible —
  those features don't exist in the models).
- Respect stated dislikes/allergies as hard filters.
- Frequency-capped, annoyance-aware, easy to decline, always explained.
- Guest-value-weighted objective; business value bounded and never dominant.
- Impulse/vulnerability protections reduce (not increase) pressure.
- No fabricated scarcity/urgency (1.7, 1.8).

---

### Change log
- v1.0 — Initial recommendation-engine specification.
